#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
实验3：一阶电路响应的研究
- 读取 RC 一阶电路零状态/零输入响应的测量数据
- 计算时间常数 τ
- 生成实验报告文本（含数据记录、截图位置提示）
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
REPORT_FILE = SCRIPT_DIR / "report_exp3.txt"

def read_exp3_data(csv_path):
    """
    读取实验三数据 CSV，预期格式如下（示例）：
    
    测量项目,数值,单位
    零状态响应_稳态值_uc(∞),4.95,V
    零状态响应_时间常数τ,19.8,us
    零输入响应_初始值_uc(0),5.02,V
    零输入响应_时间常数τ,20.2,us
    """
    df = pd.read_csv(csv_path, encoding='utf-8')
    data = {}
    for _, row in df.iterrows():
        key = row['测量项目'].strip()
        value = float(row['数值'])
        unit = row.get('单位', '').strip()
        data[key] = (value, unit)
    return data

def manual_input():
    """交互式手动输入测量数据"""
    print("\n请依次输入实验三的测量数据：")
    uc_inf = float(input("零状态响应稳态值 uc(∞) (V): "))
    tau_zs = float(input("零状态响应时间常数 τ (μs): "))
    uc0 = float(input("零输入响应初始值 uc(0) (V): "))
    tau_zi = float(input("零输入响应时间常数 τ (μs): "))
    return {
        '零状态响应_稳态值_uc(∞)': (uc_inf, 'V'),
        '零状态响应_时间常数τ': (tau_zs, 'μs'),
        '零输入响应_初始值_uc(0)': (uc0, 'V'),
        '零输入响应_时间常数τ': (tau_zi, 'μs')
    }

def generate_report(data):
    """生成实验报告文本"""
    uc_inf, unit1 = data.get('零状态响应_稳态值_uc(∞)', ('___', 'V'))
    tau_zs, unit2 = data.get('零状态响应_时间常数τ', ('___', 'μs'))
    uc0, unit3 = data.get('零输入响应_初始值_uc(0)', ('___', 'V'))
    tau_zi, unit4 = data.get('零输入响应_时间常数τ', ('___', 'μs'))

    # 理论计算（R=2kΩ, C=0.01μF => τ理论=20μs）
    tau_theory_us = 20.0  # μs

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("实验3  一阶电路响应的研究\n")
        f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        # 一、零状态响应
        f.write("一、RC 一阶电路零状态响应\n")
        f.write("-" * 60 + "\n")
        f.write(f"1. 输入信号：幅度 5V，周期 1ms，脉宽 0.5ms\n")
        f.write(f"2. 电路参数：R = 2kΩ，C = 0.01μF\n")
        f.write(f"3. 示波器测量结果：\n")
        f.write(f"   - 电容电压稳态值 uc(∞) = {uc_inf} {unit1}\n")
        f.write(f"   - 实测时间常数 τ = {tau_zs} {unit2}\n")
        f.write(f"   - 理论时间常数 τ = R·C = 2000 × 0.01e-6 = 20 μs\n")
        f.write(f"4. 误差分析：相对误差 = |{tau_zs} - {tau_theory_us}| / {tau_theory_us} × 100% = {abs(tau_zs - tau_theory_us)/tau_theory_us*100:.1f}%\n")
        f.write("5. 验证方法：从响应波形上升到 0.632Uc(∞) 处读取时间间隔。\n")
        f.write("6. 请将示波器捕获的输入信号、输出响应波形及测量 τ 的放大图粘贴至报告图3.3位置。\n\n")

        # 二、零输入响应
        f.write("二、RC 一阶电路零输入响应\n")
        f.write("-" * 60 + "\n")
        f.write(f"1. 输入信号：幅度 5V，周期 1ms，脉宽 3μs\n")
        f.write(f"2. 电路参数：R = 2kΩ，C = 0.01μF\n")
        f.write(f"3. 示波器测量结果：\n")
        f.write(f"   - 电容电压初始值 uc(0) = {uc0} {unit3}\n")
        f.write(f"   - 实测时间常数 τ = {tau_zi} {unit4}\n")
        f.write(f"   - 理论时间常数 τ = 20 μs\n")
        f.write(f"4. 误差分析：相对误差 = |{tau_zi} - {tau_theory_us}| / {tau_theory_us} × 100% = {abs(tau_zi - tau_theory_us)/tau_theory_us*100:.1f}%\n")
        f.write("5. 验证方法：从响应波形下降到 0.368Uc(0) 处读取时间间隔。\n")
        f.write("6. 请将示波器捕获的输入信号、输出响应波形及测量 τ 的放大图粘贴至报告图3.6位置。\n\n")

        # 三、实验结论
        f.write("三、实验结论\n")
        f.write("-" * 60 + "\n")
        f.write("1. 零状态响应：电容电压从 0 按指数规律上升，最终趋于电源电压（约5V）。\n")
        f.write("2. 零输入响应：电容电压从初始值按指数规律衰减到 0。\n")
        f.write("3. 实测时间常数 τ 与理论值 20μs 接近，误差主要来源于示波器光标读数精度和电容/电阻标称值的偏差。\n")
        f.write("4. 加深了对 RC 一阶电路瞬态过程的理解，掌握了时间常数的测量方法。\n")
        f.write("=" * 80 + "\n")

    print(f"实验报告文本已生成：{REPORT_FILE}")

def main():
    data_path = SCRIPT_DIR / "data.csv"
    if data_path.exists():
        print(f"发现数据文件：{data_path}，正在读取...")
        data = read_exp3_data(data_path)
    else:
        print(f"未找到 {data_path}，将采用手动输入模式。")
        data = manual_input()
    generate_report(data)

if __name__ == "__main__":
    main()