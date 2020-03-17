#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/4 10:47
# @Author  : Nelson
# @Site    : 
# @File    : get_mysql_table_detail.py
# @Software: PyCharm
'''
只需替换
database='private_lcs'
table_schema = "private_lcs"
table_structure_private_lcs.xls

可以直接使用Navicat将所有数据导出后用Excel筛选出4条数据
添加加载宏
Sub test()
    Application.ScreenUpdating = False    '禁刷新
    Dim sh As Worksheet
    For Each sh In Worksheets         '遍历工作表
        If sh.Name <> "sheet1" Then     '不等于sheet1
            rw = sh.Cells(Rows.Count, 1).End(3).Row    '最大行数
            If rw > 4 Then                        '行数大于11
                sh.Rows("2:" & (rw - 4)).Delete  '第2行到倒数第11行删除
            End If
        End If
    Next
    MsgBox "数据删除完毕！", , "提示"
    Application.ScreenUpdating = True         '刷新
End Sub


'''

import re
import time
import numpy as np
import pandas as pd
import datetime
import pymysql as ps
import pandas as pd
from warnings import filterwarnings
filterwarnings("error",category=ps.Warning)
class Shzl_Base():
    def __init__(self):
        try:
            self.db = ps.connect(host='111.14.219.169', user='root', password='3edc#EDC4rfv',port=35005,database='public_lcs',
                                 charset='utf8mb4')
            self.cursor = self.db.cursor(ps.cursors.DictCursor)
        except Exception as e:
            print('数据库连接错误', e)
    def get_table(self):
        try:
            self.cursor.execute(
                'SELECT '
                '    DISTINCT TABLE_NAME '
                '    FROM INFORMATION_SCHEMA.tables '
                '        WHERE table_schema = "public_lcs" '
                # '        and TABLE_NAME like "T_%";'
            )
            data = self.cursor.fetchall()
            return data
        except Exception as e:
            print(e)
            self.db.rollback()
    def get_table_comment(self,table):
        try:
            self.cursor.execute(
                'Select '
                '    TABLE_COMMENT 表注释 '
                '        from INFORMATION_SCHEMA.TABLES '
                '            Where table_schema = "private_lcs"'
                '            AND table_name ="{}"'.format(table)
            )
            data = self.cursor.fetchall()
            return data
        except Exception as e:
            print(e)
            self.db.rollback()

    def get_table_count(self,table):
        try:
            self.cursor.execute(
                'Select '
                '    count(*) row_sum '
                '        from {} '.format(table)
            )
            data = self.cursor.fetchall()
            return data
        except Exception as e:
            print(e)
            self.db.rollback()

    def get_table_detail(self,table):
        try:
            self.cursor.execute(
                ' show create table {}'.format(table)
            )
            data = self.cursor.fetchall()
            return data
        except Exception as e:
            print(e)
            self.db.rollback()

def get_table_text(table):
    field_text = re.compile(r'[(](.*)[)]', re.S)
    field = re.compile(r"`(.*)`")
    field_name_sub = re.compile(r"((?<=COMMENT ').*?(?=\'))")
    # field_length = re.compile(r"((?<=\()[0-9]\d+(?=\)))")
    field_length = re.compile(r"((?<=\()[0-9].*?(?=\)))")
    field_type = re.compile(r" int|varchar| date |datetime| timestamp | text |decimal|bigint|tinyint|blob")
    # if len(re.findall(field_text,table))!=0:
    # print(re.findall(field_text,table)[0])
    try:
        key_value = re.findall(r'PRIMARY KEY \(\`(.*)\`\)',str(re.findall(field_text,table)[0]))[0]
    except:
        key_value=''
    # print(key_value)
    list = re.split(',\n',re.findall(field_text,table)[0])#每个字段必须定义完换行
    table_b = []
    table_c = []
    table_b.append('序号')
    table_b.append('字段名')
    table_b.append('数据项名称')
    table_b.append('类型')
    table_b.append('长度')
    table_b.append('备注')
    table_c.append(table_b)
    # print('-----------------')
    # print(re.findall(field_type,str(list)))
    # print('-----------------')
    # print(len(re.findall(field_type,str(list))))
    for i in range(len(re.findall(field_type,str(list)))):
        table_d = []
        table_d.append(str(i+1))
        # if len(re.findall(field, list[i])) != 0:
        #     print('-----------------')
        #     print(re.findall(field, list[i])[0])
        #     print('-----------------')
        # print('-----------------')
        # print(re.findall(field,list[i]))
        # print('-----------------')
        table_d.append(str('' if len(re.findall(field,list[i]))==0 else re.findall(field,list[i])[0]))
        # table_d.append(str('' if len(re.findall(field_name_sub,list[i]))==0 else (re.findall(field_name_sub,list[i])[0] if i+1!=1 else '自增主键')))
        table_d.append(str('' if len(re.findall(field_name_sub,list[i]))==0 else (re.findall(field_name_sub,list[i])[0])))
        table_d.append(str('' if len(re.findall(field_type,list[i]))==0 else re.findall(field_type,list[i])[0]))
        table_d.append(str('' if len(re.findall(field_length,list[i]))==0 else re.findall(field_length,list[i])[0]))
        # table_d.append(str('' if i + 1 != 1 else '主键'))
        if key_value==re.findall(field,list[i])[0]:
            table_d.append('主键')
            # print('主键')
        else:
            table_d.append('')
            # table_d.append(re.findall(field_length, list[i])[0])
        # print(str('主键' if len(re.findall(key_value,list[i]))==0 else re.findall(key_value,list[i])[0]))
        # table_d.append(str('主键' if len(re.findall(field_length,list[i]))==0 else re.findall(field_length,list[i])[0]))
        #判断是否为主键
        table_c.append(table_d)
    return table_c

#若少行则需要看字段类型是否出现以上没有的
def get_mysql_table_detail(shzl):
    tables = shzl.get_table()
    write_file = open('table_structure_private_lcs.xls',mode='w',encoding='GBK')
    for table in tables:
        if table['TABLE_NAME'] not in ['TABLE_total','T_3070020000022_000555test']:
            # if table['TABLE_NAME'] =='T_3070020000010_000023':
            print(table['TABLE_NAME'])
            comment = shzl.get_table_comment(table['TABLE_NAME'])
            # row_sum = shzl.get_table_count(table['TABLE_NAME'])
            # print(str(table['TABLE_NAME'])+'\t'+str(comment[0]['表注释'])+'\t'+str(row_sum[0]['row_sum'])+'\n')
            # write_file.write(str(table['TABLE_NAME'])+'\t'+str(comment[0]['表注释'])+'\t'+str(row_sum[0]['row_sum'])+'\n')
            write_file.write(str(table['TABLE_NAME'])+'\t'+str(comment[0]['表注释'])+'\n')
            table_detail = shzl.get_table_detail(table['TABLE_NAME'])
            table_text = (table_detail[0]['Create Table'])
            for i in get_table_text(table_text):
                    # print(str(i[0]) + '\t' + str(i[1]) + '\t' + str(i[2]) + '\t' + str(i[3]) + '\t' + str(
                    #     i[4]) + '\t' + str(i[5]) + '\n')
                write_file.write(str(i[0]) + '\t' + str(i[1]) + '\t' + str(i[2]) + '\t' + str(i[3]) + '\t' + str(
                    i[4]) + '\t' + str(i[5]) + '\n')
            write_file.write('\n')
    write_file.close()

if __name__ == '__main__':
    shzl = Shzl_Base()
    get_mysql_table_detail(shzl)
