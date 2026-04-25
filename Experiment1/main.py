import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from scipy.interpolate import make_interp_spline
import os

# 基础设置：确保中文显示与科研风格
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('seaborn-v0_8-muted') 

def process_experiment_1():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'exp_1.csv')
    
    if not os.path.exists(csv_path):
        print(f"错误：未找到 {csv_path}")
        return

    try:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
    except:
        df = pd.read_csv(csv_path, encoding='gbk')

    def get_row(name):
        return df[df['Project'] == name].iloc[0, 1:].dropna().values.astype(float)

    # --- 1. 数据提取 ---
    v_linear = get_row('Linear_V')
    i_linear = get_row('Linear_I')
    v_nonlin = get_row('NonLinear_V')
    i_nonlin = get_row('NonLinear_I')
    i_ideal = get_row('IdealSource_I')
    v_ideal = get_row('IdealSource_V')
    i_actual = get_row('ActualSource_I')
    v_actual = get_row('ActualSource_V')

    # --- 2. 绘图部分（按照实验报告要求分为三张图） ---

    # 图 1：线性电阻伏安特性
    plt.figure(figsize=(8, 5), dpi=300)
    plt.scatter(v_linear, i_linear, color='#1f77b4', marker='o', s=50, label='测量点', zorder=5)
    slope, intercept, r_v, _, _ = linregress(v_linear, i_linear)
    v_fit = np.linspace(min(v_linear), max(v_linear), 100)
    plt.plot(v_fit, slope*v_fit + intercept, color='#1f77b4', ls='--', alpha=0.7, label=f'线性拟合 (R={1000/slope:.1f}Ω)')
    plt.title('图1.1 线性电阻伏安特性曲线', fontsize=12)
    plt.xlabel('电压 U (V)')
    plt.ylabel('电流 I (mA)')
    plt.legend()
    plt.grid(True, ls=':', alpha=0.5)
    plt.savefig(os.path.join(base_dir, '1_Linear_Resistor.png'))

    # 图 2：非线性电阻（二极管）伏安特性
    plt.figure(figsize=(8, 5), dpi=300)
    plt.scatter(v_nonlin, i_nonlin, color='#d62728', marker='x', s=50, label='测量点', zorder=5)
    if len(v_nonlin) > 3:
        v_smooth = np.linspace(v_nonlin.min(), v_nonlin.max(), 300)
        spl = make_interp_spline(v_nonlin, i_nonlin, k=3) # 三次样条插值
        plt.plot(v_smooth, spl(v_smooth), color='#d62728', lw=2, label='二极管特性曲线(平滑)')
    plt.title('图1.2 非线性电阻（二极管）伏安特性曲线', fontsize=12)
    plt.xlabel('电压 U (V)')
    plt.ylabel('电流 I (mA)')
    plt.legend()
    plt.grid(True, ls=':', alpha=0.5)
    plt.savefig(os.path.join(base_dir, '2_Diode_Characteristic.png'))

    # 图 3：电压源外特性对比
    plt.figure(figsize=(8, 5), dpi=300)
    plt.plot(i_ideal, v_ideal, color='#2ca02c', marker='o', lw=2, label='理想电压源 (Us=10V)')
    plt.plot(i_actual, v_actual, color='#ff7f0e', marker='s', lw=2, label='实际电压源 (含内阻Rs)')
    s_slope, _, _, _, _ = linregress(i_actual, v_actual)
    rs_ohm = abs(s_slope) * 1000
    plt.title('图1.3 理想与实际电压源外特性对比', fontsize=12)
    plt.xlabel('电流 I (mA)')
    plt.ylabel('电压 U (V)')
    plt.ylim(0, max(v_ideal)*1.2)
    plt.legend()
    plt.grid(True, ls=':', alpha=0.5)
    plt.savefig(os.path.join(base_dir, '3_Voltage_Source_Comparison.png'))

    # --- 3. 生成抄写手册 ---
    with open(os.path.join(base_dir, 'report_copy_exp1.txt'), 'w', encoding='utf-8') as f:
        f.write("【实验一：基本元件伏安特性的测绘 - 直接抄写手册】\n")
        f.write("="*60 + "\n\n")

        f.write("1. 线性电阻数据（表1.1）\n")
        f.write(f"U (V) | {' | '.join([f'{x:5.1f}' for x in v_linear])}\n")
        f.write(f"I (mA)| {' | '.join([f'{x:5.1f}' for x in i_linear])}\n\n")

        f.write("2. 非线性电阻（二极管）数据（表1.2）\n")
        f.write(f"U (V) | {' | '.join([f'{x:5.2f}' for x in v_nonlin])}\n")
        f.write(f"I (mA)| {' | '.join([f'{x:5.1f}' for x in i_nonlin])}\n\n")

        f.write("3. 理想与实际电压源数据（表1.3 & 1.4）\n")
        f.write(f"I (mA)| {' | '.join([f'{x:5.1f}' for x in i_ideal])}\n")
        f.write(f"U理想 | {' | '.join([f'{x:5.1f}' for x in v_ideal])}\n")
        f.write(f"U实际 | {' | '.join([f'{x:5.1f}' for x in v_actual])}\n\n")

        f.write("4. 实验结论及总结（直接抄写）\n")
        f.write("-" * 50 + "\n")
        f.write(f"a) 线性电阻：其伏安特性曲线为过原点的直线，阻值不随电压变化，符合欧姆定律。拟合 R = {1000/slope:.1f}Ω。\n")
        f.write("b) 非线性电阻：二极管具有单向导电性，仅在正向电压超过开启电压（约0.5-0.7V）后导通，电流呈指数增长。\n")
        f.write(f"c) 电压源：理想电压源输出恒定；实际电压源受内阻 Rs (约{rs_ohm:.1f}Ω) 影响，电压随电流增大线性下降。\n")

    print("已成功生成三幅高清图表和抄写手册！")

if __name__ == "__main__":
    process_experiment_1()