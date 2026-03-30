#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author：wangxijie
@date：2026-03-12

Excel按日拆分工具脚本。
功能：读取Excel文件的全部sheet，把每个sheet按第一列（日期）拆分为多个带表头的txt文件。
将相同日期的数据放到同一个以日期命名的文件夹中。
"""

import os
import sys
import pandas as pd
from datetime import datetime

def split_excel_by_date(input_excel, output_base_dir, batch_no='04'):
    if not os.path.exists(input_excel):
        print(f"Error: 找不到文件 {input_excel}")
        sys.exit(1)
        
    os.makedirs(output_base_dir, exist_ok=True)
    
    try:
        xls = pd.ExcelFile(input_excel)
    except Exception as e:
        print(f"Error: 无法读取Excel文件 {input_excel}. 详情: {e}")
        sys.exit(1)
        
    for sheet_name in xls.sheet_names:
        print(f"正在处理 Sheet: {sheet_name}...")
        try:
            # 读取时设置 header=1，即取第二行作为列的 Header (索引从 0 开始, header=1 表示第2行)
            df = pd.read_excel(input_excel, sheet_name=sheet_name, header=1)
        except Exception as e:
            print(f"  警告: 无法读取 sheet '{sheet_name}'. 跳过。详情: {e}")
            continue
            
        if df.empty:
            print(f"  提示: sheet '{sheet_name}' 是空的。跳过。")
            continue
            
        # 强制设置第一列的名称为 "交易日期"
        cols = list(df.columns)
        cols[0] = '交易日期'
        df.columns = cols
        
        # 将第一列作为日期列进行操作
        date_col_name = df.columns[0]
        
        # 强制转换为日期类型，无法识别的值全变为 NaT (Not a Time)
        df[date_col_name] = pd.to_datetime(df[date_col_name], errors='coerce')
        
        # 移除日期列值为NaT的行（即非日期的非法值及原本的空行）
        df = df.dropna(subset=[date_col_name])
        if df.empty:
            print(f"  提示: sheet '{sheet_name}' 在清理无效日期行后为空。跳过。")
            continue
            
        # 强制第一列日期数据的格式为 YYYYMMDD
        df[date_col_name] = df[date_col_name].dt.strftime('%Y%m%d')
            
        # 将无数据的字段用0填充
        df = df.fillna(0)

        # 提取所有数值类型的列（除了第一列日期，因为日期之前已被转为字符串）
        # 元转分：所有数值列乘以100并取整
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            df[col] = (df[col] * 100).round().astype(int)
            
        grouped = df.groupby(date_col_name)
        
        for date_val, group_df in grouped:
            
            # 由于已在之前用 strftime 格式化过，当前 date_val 一定是形如 '20251106' 的字符串
            date_str = str(date_val)
                
            # 月份或日期的输出路径
            output_dir = os.path.join(output_base_dir, date_str)
            os.makedirs(output_dir, exist_ok=True)
            
            # 删除 sheet_name 中的 "网联" 二字
            clean_sheet_name = sheet_name.replace('网联', '')
            
            # 命名格式: 991100001624_XTON_日期_sheet名称_批次号.txt (sheet名称已剔除特殊词)
            file_name = f"991100001624_XTON_{date_str}_{clean_sheet_name}_{batch_no}.txt"
            output_file_path = os.path.join(output_dir, file_name)
            try:
                # 定义并写入特定的首行
                first_line = f"1.0.0|991100001624|911100000005|1|{date_str}|{date_str}\n"
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    f.write(first_line)
                    
                # 将该日期下的数据以|作为分隔符，追加至文件中（不覆盖首行，从第二行开始写表头和内容）
                group_df.to_csv(output_file_path, sep='|', index=False, float_format='%g', mode='a')
                print(f"  - 成功拆分并保存: 日期={date_str}, 记录数={len(group_df)} -> {output_file_path}")
            except Exception as e:
                print(f"  - 错误: 无法保存日期={date_str} 的数据。详情: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python split_excel.py <输入的Excel文件路径> <输出目录路径> [批次号]")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_directory = sys.argv[2]
    
    # 获取可选的批次号参数，默认为 '04'
    batch_num = sys.argv[3] if len(sys.argv) > 3 else '04'
    
    print(f"=== 开始执行Excel按日拆分 (批次号: {batch_num}) ===")
    split_excel_by_date(input_file, output_directory, batch_num)
    print(f"=== 拆分完成 ===")
