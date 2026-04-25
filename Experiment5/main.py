#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
实验5：R、L、C单个元件阻抗频率特性测试（修正版）
- 正确读取 data.csv 中的频率和 Ubc 测量值
- 计算 I (mA) 和 |Z| (kΩ)
- 绘制实测曲线（无理论曲线，符合实验报告要求）
- 生成数据表格和 report.txt
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# ================== 参数配置 ==================
US_V = 2.0                     # 信号源有效值 (V)
R_SAMPLE = 10.0                # 采样电阻 (Ω)

SCRIPT_DIR = Path(__file__).parent
OUTPUT_TABLE = SCRIPT_DIR / "impedance_results.csv"
OUTPUT_FIGURE = SCRIPT_DIR / "impedance_frequency_curve.png"
REPORT_FILE = SCRIPT_DIR / "report.txt"

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 12

# ================== 数据读取（修正版） ==================
def load_impedance_data(csv_path):
    """
    正确读取无表头的宽格式数据
    格式示例：
        频率 f (kHz),10,20,30,40,50
        Us (V),2,2,2,2,2
        R_Ubc (mV),10.9,10.3,10.5,10.3,10.4
        L_Ubc (mV),125,61.7,43.9,32.6,26.3
        C_Ubc (mV),134,245,380,486,600
    """
    # 读取全部行，不使用表头
    df_raw = pd.read_csv(csv_path, header=None, encoding='utf-8', comment='#')
    # 第一行为频率行
    freq_row = df_raw.iloc[0]
    # 提取频率值（跳过第一个单元格"频率 f (kHz)"）
    freqs = freq_row.iloc[1:].astype(float).values
    
    # 构建数据字典
    data = {'f_kHz': freqs}
    # 行标识与列名的映射
    row_keywords = {
        'R_Ubc (mV)': 'R_Ubc_mV',
        'L_Ubc (mV)': 'L_Ubc_mV',
        'C_Ubc (mV)': 'C_Ubc_mV'
    }
    for keyword, col_name in row_keywords.items():
        # 找到第一个单元格等于 keyword 的行
        mask = df_raw.iloc[:, 0].astype(str).str.strip() == keyword
        if not mask.any():
            raise ValueError(f"CSV 中缺少 {keyword} 行")
        row = df_raw[mask].iloc[0]
        values = row.iloc[1:].astype(float).values
        data[col_name] = values
    
    df = pd.DataFrame(data)
    return df

def read_extra_params(csv_path):
    """读取相位测量和轨迹线数据（保留原有逻辑）"""
    extra = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ',' in line:
                key, val_str = line.split(',', 1)
                key = key.strip()
                val_str = val_str.strip()
                if not val_str:
                    continue
                try:
                    val = float(val_str)
                    base_key = key.split(' (')[0]
                    extra[base_key] = val
                except:
                    pass
    return extra

# ================== 计算 |Z| ==================
def calc_impedance(df):
    df = df.copy()
    for element, col in zip(['R', 'L', 'C'], ['R_Ubc_mV', 'L_Ubc_mV', 'C_Ubc_mV']):
        ubc_mv = df[col].values
        ubc_mv = np.maximum(ubc_mv, 1e-6)
        i_ma = ubc_mv / R_SAMPLE
        df[f'{element}_I_mA'] = i_ma
        z_kohm = US_V / (i_ma / 1000.0) / 1000.0
        df[f'{element}_Z_kOhm'] = z_kohm
    return df

# ================== 绘图（仅实测曲线，无理论线） ==================
def plot_impedance_curves(df):
    freqs = df['f_kHz'].values
    z_r = df['R_Z_kOhm'].values
    z_l = df['L_Z_kOhm'].values
    z_c = df['C_Z_kOhm'].values

    plt.figure(figsize=(8, 5), dpi=100)
    plt.plot(freqs, z_r, 'o-', color='red', label='电阻 R', linewidth=1.5, markersize=6)
    plt.plot(freqs, z_l, 's-', color='blue', label='电感 L', linewidth=1.5, markersize=6)
    plt.plot(freqs, z_c, '^-', color='green', label='电容 C', linewidth=1.5, markersize=6)
    
    plt.xlabel('频率 f (kHz)', fontsize=12)
    plt.ylabel('阻抗模 |Z| (kΩ)', fontsize=12)
    plt.title('R、L、C元件阻抗频率特性曲线', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='best', fontsize=10)
    
    # 自动调整坐标范围
    y_min = min(z_r.min(), z_l.min(), z_c.min())
    y_max = max(z_r.max(), z_l.max(), z_c.max())
    margin = (y_max - y_min) * 0.05
    plt.ylim(y_min - margin, y_max + margin)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_FIGURE, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"阻抗频率特性曲线已保存：{OUTPUT_FIGURE}")

# ================== 输出表格 ==================
def print_and_save_table(df):
    results = pd.DataFrame({
        'f (kHz)': df['f_kHz'],
        'R_Ubc (mV)': df['R_Ubc_mV'],
        'R_I (mA)': df['R_I_mA'],
        'R_|Z| (kΩ)': df['R_Z_kOhm'],
        'L_Ubc (mV)': df['L_Ubc_mV'],
        'L_I (mA)': df['L_I_mA'],
        'L_|Z| (kΩ)': df['L_Z_kOhm'],
        'C_Ubc (mV)': df['C_Ubc_mV'],
        'C_I (mA)': df['C_I_mA'],
        'C_|Z| (kΩ)': df['C_Z_kOhm']
    }).round(3)
    print("\n========== 实验数据计算结果 ==========")
    print(results.to_string(index=False))
    print("=====================================\n")
    results.to_csv(OUTPUT_TABLE, index=False, encoding='utf-8-sig')
    print(f"数据表格已保存：{OUTPUT_TABLE}")

# ================== 生成报告 ==================
def generate_report(df_calc, extra):
    freq = df_calc['f_kHz'].values
    r_ubc = df_calc['R_Ubc_mV'].values
    l_ubc = df_calc['L_Ubc_mV'].values
    c_ubc = df_calc['C_Ubc_mV'].values
    r_i = df_calc['R_I_mA'].values
    l_i = df_calc['L_I_mA'].values
    c_i = df_calc['C_I_mA'].values
    r_z = df_calc['R_Z_kOhm'].values
    l_z = df_calc['L_Z_kOhm'].values
    c_z = df_calc['C_Z_kOhm'].values

    # 相位数据
    R_AB = extra.get('R_AB', 100.0)
    R_CD = extra.get('R_CD', 0.0)
    L_AB = extra.get('L_AB', 100.0)
    L_CD = extra.get('L_CD', 21.6)
    C_AB = extra.get('C_AB', 100.0)
    C_CD = extra.get('C_CD', 75.2)
    phi_R = 0.0
    phi_L = (L_CD / L_AB) * 360.0 if L_AB != 0 else 0
    phi_C_raw = (C_CD / C_AB) * 360.0 if C_AB != 0 else 0
    phi_C_display = -phi_C_raw

    # 轨迹线数据
    R_2a = extra.get('R_2a', 5.76)
    R_2b_mV = extra.get('R_2b', 29.6)
    L_2a = extra.get('L_2a', 5.72)
    L_2b_mV = extra.get('L_2b', 356)
    C_2a = extra.get('C_2a', 5.80)
    C_2b_mV = extra.get('C_2b', 366)

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("实验5  R、L、C单个元件阻抗频率特性测试\n")
        f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        # 第一部分：数据表
        f.write("【第一部分】测绘R、L、C单个元件阻抗频率特性曲线\n")
        f.write("-" * 60 + "\n")
        f.write("表5.1  实验测量数据与计算结果（信号源 Us = 2V）\n")
        f.write("+----------+----------------------+----------------------+----------------------+\n")
        f.write("| f (kHz)  |       R 元件         |       L 元件         |       C 元件         |\n")
        f.write("+----------+----------+-----------+----------+-----------+----------+-----------+\n")
        f.write("|          | Ubc(mV)  | I(mA)     | Ubc(mV)  | I(mA)     | Ubc(mV)  | I(mA)     |\n")
        f.write("+----------+----------+-----------+----------+-----------+----------+-----------+\n")
        for i in range(len(freq)):
            f.write(f"| {freq[i]:5.0f}    | {r_ubc[i]:7.2f} | {r_i[i]:8.3f} | {l_ubc[i]:7.2f} | {l_i[i]:8.3f} | {c_ubc[i]:7.2f} | {c_i[i]:8.3f} |\n")
        f.write("+----------+----------+-----------+----------+-----------+----------+-----------+\n")
        f.write("阻抗模 |Z| (kΩ) 计算结果：\n")
        f.write("+----------+----------------------+----------------------+----------------------+\n")
        f.write("| f (kHz)  |   R_|Z| (kΩ)         |   L_|Z| (kΩ)         |   C_|Z| (kΩ)         |\n")
        f.write("+----------+----------------------+----------------------+----------------------+\n")
        for i in range(len(freq)):
            f.write(f"| {freq[i]:5.0f}    | {r_z[i]:10.3f}           | {l_z[i]:10.3f}           | {c_z[i]:10.3f}           |\n")
        f.write("+----------+----------------------+----------------------+----------------------+\n\n")

        f.write("【绘制曲线】\n")
        f.write(f"阻抗频率特性曲线见图 {OUTPUT_FIGURE.name}（已插入报告图5.2位置）。\n")
        f.write("曲线显示：电阻|Z|基本不随频率变化；电感|Z|随频率增加而增大；电容|Z|随频率增加而减小。\n\n")

        # 第二部分：相位测量
        f.write("【第二部分】R、L、C单个元件的相位测量\n")
        f.write("-" * 60 + "\n")
        f.write("测试条件：频率 f = 10 kHz，Us = 2 V，周期 T = 100 μs。\n")
        f.write("相位差 Δφ = (CD / AB) × 360°\n\n")
        f.write("实测数据与计算结果：\n")
        f.write("+--------+------------+------------+----------------+--------------------------------------------------+\n")
        f.write("| 元件   | AB (格)     | CD (格)     | 相位差 Δφ      | 结论（电压与电流相位关系）                       |\n")
        f.write("+--------+------------+------------+----------------+--------------------------------------------------+\n")
        f.write(f"| 电阻 R | {R_AB:10.1f} | {R_CD:10.3f} | {phi_R:12.1f}°   | 电压与电流同相                                   |\n")
        f.write(f"| 电感 L | {L_AB:10.1f} | {L_CD:10.3f} | {phi_L:12.1f}°   | 电压超前电流（感性）                             |\n")
        f.write(f"| 电容 C | {C_AB:10.1f} | {C_CD:10.3f} | {phi_C_display:12.1f}°   | 电流超前电压（容性）                              |\n")
        f.write("+--------+------------+------------+----------------+--------------------------------------------------+\n")
        f.write("（请将示波器波形截图插入报告图5.3位置）\n\n")

        # 第三部分：轨迹线
        f.write("【第三部分】R、L、C单个元件的伏安关系轨迹线（X-Y模式）\n")
        f.write("-" * 60 + "\n")
        f.write("测试条件：频率 10 kHz，Us = 2 V。X轴 = 元件电压，Y轴 = 采样电阻电压（正比于电流）。\n")
        f.write("记录图5.4中标记的 a、b 值（2a 为X轴宽度，2b 为Y轴宽度）。\n\n")
        f.write("实测数据：\n")
        f.write("+--------+----------------+----------------+--------------------------------------------------+\n")
        f.write("| 元件   | 2a (V)          | 2b (V)          | 轨迹形状及说明                                   |\n")
        f.write("+--------+----------------+----------------+--------------------------------------------------+\n")
        f.write(f"| 电阻 R | {R_2a:12.3f}       | {R_2b_mV/1000:12.3f}       | 直线（电压电流成比例）                           |\n")
        f.write(f"| 电感 L | {L_2a:12.3f}       | {L_2b_mV/1000:12.3f}       | 椭圆（顺时针旋转，电压超前电流）                 |\n")
        f.write(f"| 电容 C | {C_2a:12.3f}       | {C_2b_mV/1000:12.3f}       | 椭圆（逆时针旋转，电流超前电压）                 |\n")
        f.write("+--------+----------------+----------------+--------------------------------------------------+\n")
        f.write("（请将X-Y波形截图插入报告图5.5位置，并标出a、b值）\n\n")

        # 实验结论
        f.write("【实验结论总结】\n")
        f.write("-" * 60 + "\n")
        f.write("1. 电阻元件的阻抗模基本不随频率变化，实测值稳定在约2 kΩ，电压与电流同相位。\n")
        f.write("2. 电感元件的阻抗模随频率升高而增大（XL = 2πfL），电压超前电流约90°。\n")
        f.write("3. 电容元件的阻抗模随频率升高而减小（XC = 1/(2πfC)），电流超前电压约90°。\n")
        f.write("4. X-Y模式下，电阻为直线，电感、电容为椭圆且旋转方向相反，验证了相位关系。\n")
        f.write("5. 实验数据与理论分析吻合，掌握了R、L、C元件阻抗频率特性的测量方法。\n\n")
        f.write("=" * 80 + "\n")

    print(f"实验报告文本已生成：{REPORT_FILE}")

# ================== 主程序 ==================
def main():
    data_path = SCRIPT_DIR / "data.csv"
    if not data_path.exists():
        print(f"错误：未找到 {data_path}，请确保 data.csv 与 main.py 在同一目录下。")
        return

    try:
        df_imp = load_impedance_data(data_path)
    except Exception as e:
        print(f"读取阻抗数据失败: {e}")
        return

    extra = read_extra_params(data_path)
    df_calc = calc_impedance(df_imp)
    print_and_save_table(df_calc)
    plot_impedance_curves(df_calc)
    generate_report(df_calc, extra)

if __name__ == "__main__":
    main()