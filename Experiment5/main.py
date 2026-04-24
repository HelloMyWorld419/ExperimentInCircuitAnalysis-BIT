"""
实验5：R、L、C单个元件阻抗频率特性测试
- 读取data.csv中的Ubc测量值（mV）
- 计算通过元件的电流Iab (mA) 和阻抗模|Z| (kΩ)
- 绘制测量点与理论曲线对比图（同一坐标轴）
- 输出数据表格，保存图片和计算结果
- 生成report.txt，包含实验报告所有需要填写的数据和结论模板
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# ================== 参数配置 ==================
US_V = 2.0                     # 信号源有效值 (V)
R_SAMPLE = 10.0                # 采样电阻 (Ω)
R_NOM = 2000.0                 # 电阻标称值 (Ω)
L_NOM = 2.7e-3                 # 电感标称值 (H)
C_NOM = 0.1e-6                 # 电容标称值 (F)

# 获取当前脚本所在目录
SCRIPT_DIR = Path(__file__).parent

# 输出文件路径
OUTPUT_TABLE = SCRIPT_DIR / "impedance_results.csv"
OUTPUT_FIGURE = SCRIPT_DIR / "impedance_frequency_curve.png"
REPORT_FILE = SCRIPT_DIR / "report.txt"

# 设置matplotlib中文字体（若系统无中文字体，可注释或改为英文）
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ================== 数据读取 ==================
def load_data(csv_path):
    """读取CSV数据，返回DataFrame"""
    df = pd.read_csv(csv_path)
    required_cols = ['f_kHz', 'R_Ubc_mV', 'L_Ubc_mV', 'C_Ubc_mV']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"缺少列：{col}")
    return df

# ================== 计算 |Z| ==================
def calc_impedance(df):
    """
    根据 Ubc_mV 计算：
    I_mA = Ubc_mV / 10
    |Z|_kΩ = 2 / I_mA = 20 / Ubc_mV
    """
    df = df.copy()
    for element, col in zip(['R', 'L', 'C'], ['R_Ubc_mV', 'L_Ubc_mV', 'C_Ubc_mV']):
        ubc_mv = df[col].values
        ubc_mv = np.maximum(ubc_mv, 1e-6)  # 避免除零
        i_ma = ubc_mv / R_SAMPLE
        df[f'{element}_I_mA'] = i_ma
        z_kohm = US_V / (i_ma / 1000.0) / 1000.0
        df[f'{element}_Z_kOhm'] = z_kohm
    return df

# ================== 理论曲线函数 ==================
def theoretical_resistance(f_khz):
    return np.full_like(f_khz, R_NOM / 1000.0)

def theoretical_inductance(f_khz):
    f_hz = f_khz * 1000.0
    return (2 * np.pi * f_hz * L_NOM) / 1000.0

def theoretical_capacitance(f_khz):
    f_hz = f_khz * 1000.0
    return 1.0 / (2 * np.pi * f_hz * C_NOM) / 1000.0

# ================== 绘图 ==================
def plot_impedance_curves(df):
    freqs = df['f_kHz'].values
    f_smooth = np.linspace(freqs.min(), freqs.max(), 200)
    
    plt.figure(figsize=(10, 6))
    # 电阻
    z_r_meas = df['R_Z_kOhm'].values
    plt.plot(freqs, z_r_meas, 'o-', color='red', label='电阻 (测量)', markersize=6, linewidth=1.5)
    plt.plot(f_smooth, theoretical_resistance(f_smooth), '--', color='red', alpha=0.7, label='电阻 (理论)')
    # 电感
    z_l_meas = df['L_Z_kOhm'].values
    plt.plot(freqs, z_l_meas, 's-', color='blue', label='电感 (测量)', markersize=6, linewidth=1.5)
    plt.plot(f_smooth, theoretical_inductance(f_smooth), '--', color='blue', alpha=0.7, label='电感 (理论)')
    # 电容
    z_c_meas = df['C_Z_kOhm'].values
    plt.plot(freqs, z_c_meas, '^-', color='green', label='电容 (测量)', markersize=6, linewidth=1.5)
    plt.plot(f_smooth, theoretical_capacitance(f_smooth), '--', color='green', alpha=0.7, label='电容 (理论)')
    
    plt.xlabel('频率 f (kHz)', fontsize=12)
    plt.ylabel('阻抗模 |Z| (kΩ)', fontsize=12)
    plt.title('R、L、C元件阻抗频率特性曲线', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='best', fontsize=10)
    
    all_z = np.concatenate([z_r_meas, z_l_meas, z_c_meas,
                            theoretical_resistance(f_smooth),
                            theoretical_inductance(f_smooth),
                            theoretical_capacitance(f_smooth)])
    y_min, y_max = all_z.min(), all_z.max()
    margin = (y_max - y_min) * 0.05
    plt.ylim(y_min - margin, y_max + margin)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_FIGURE, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"图表已保存为：{OUTPUT_FIGURE}")

# ================== 输出第一部分表格（控制台和CSV）==================
def print_and_save_table(df):
    freq = df['f_kHz']
    results = pd.DataFrame({
        'f (kHz)': freq,
        'R_Ubc (mV)': df['R_Ubc_mV'],
        'R_I (mA)': df['R_I_mA'],
        'R_|Z| (kΩ)': df['R_Z_kOhm'],
        'L_Ubc (mV)': df['L_Ubc_mV'],
        'L_I (mA)': df['L_I_mA'],
        'L_|Z| (kΩ)': df['L_Z_kOhm'],
        'C_Ubc (mV)': df['C_Ubc_mV'],
        'C_I (mA)': df['C_I_mA'],
        'C_|Z| (kΩ)': df['C_Z_kOhm']
    })
    results = results.round(3)
    print("\n========== 实验数据计算结果 ==========")
    print(results.to_string(index=False))
    print("=====================================\n")
    results.to_csv(OUTPUT_TABLE, index=False)
    print(f"数据表格已保存为：{OUTPUT_TABLE}")

# ================== 生成实验报告文本 ==================
def generate_report(df_calc):
    """生成report.txt，包含实验报告所有需要填写的数据和结论模板"""
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

    # 理论值（用于对比）
    r_theo = theoretical_resistance(freq)
    l_theo = theoretical_inductance(freq)
    c_theo = theoretical_capacitance(freq)

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("实验5  R、L、C单个元件阻抗频率特性测试\n")
        f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        # ---- 第一部分：阻抗频率特性曲线 ----
        f.write("【第一部分】测绘R、L、C单个元件阻抗频率特性曲线\n")
        f.write("-" * 60 + "\n")
        f.write("表5.1  实验测量数据与计算结果（信号源 Us = 2V）\n")
        # 简单表格形式
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

        f.write("【理论对比】\n")
        f.write("元件      | 理论阻抗模 | 测量值范围 (kΩ) | 结论\n")
        f.write("----------+------------+----------------+-----------------------------------\n")
        f.write(f"电阻 (R)  | {r_theo[0]:.2f} kΩ (恒定) | {r_z.min():.3f} ~ {r_z.max():.3f} | 基本恒定，符合欧姆定律\n")
        f.write(f"电感 (L)  | 2πfL，随频率线性增加 | {l_z.min():.3f} ~ {l_z.max():.3f} | 阻抗随频率升高而增大\n")
        f.write(f"电容 (C)  | 1/(2πfC)，随频率反比减小 | {c_z.min():.3f} ~ {c_z.max():.3f} | 阻抗随频率升高而减小\n\n")

        f.write("【绘制曲线】\n")
        f.write(f"参见生成的图片：{OUTPUT_FIGURE.name}（请插入报告图5.2位置）\n\n")

        # ---- 第二部分：相位测量（填空模板）----
        f.write("【第二部分】R、L、C单个元件的相位测量\n")
        f.write("-" * 60 + "\n")
        f.write("测试条件：信号源频率 f = 10 kHz，有效值 Us = 2 V\n")
        f.write("示波器CH1测量元件电压（AC间），CH2测量采样电阻电压（BC间，代表电流）。\n")
        f.write("测量两通道波形的时间差 Δt，计算相位差 Δφ = (Δt / T) × 360°，其中 T = 0.1 ms（10 kHz）。\n\n")
        f.write("请根据实验记录填写下表：\n")
        f.write("+--------+----------------+----------------+--------------------------------------------------+\n")
        f.write("| 元件   | Δt (μs)        | 相位差 Δφ      | 结论（电压与电流的相位关系）                      |\n")
        f.write("+--------+----------------+----------------+--------------------------------------------------+\n")
        f.write("| 电阻 R | ______________ | ___________°   | 电压与电流同相（0°）                              |\n")
        f.write("| 电感 L | ______________ | ___________°   | 电压超前电流 90°（感性）                          |\n")
        f.write("| 电容 C | ______________ | ___________°   | 电流超前电压 90°（容性）                          |\n")
        f.write("+--------+----------------+----------------+--------------------------------------------------+\n")
        f.write("注：若示波器直接读取相位差，直接填入即可。\n\n")
        f.write("（请将示波器波形截图插入报告图5.3位置）\n\n")

        # ---- 第三部分：伏安关系轨迹线（填空模板）----
        f.write("【第三部分】R、L、C单个元件的伏安关系轨迹线（X-Y模式）\n")
        f.write("-" * 60 + "\n")
        f.write("测试条件：频率 10 kHz，Us = 2 V。示波器 X-Y 方式，X轴 = 元件电压，Y轴 = 采样电阻电压（正比于电流）。\n")
        f.write("记录图5.4中标记的 a、b 值（2a 为X轴方向宽度，2b 为Y轴方向宽度，单位：格 × 伏/格）。\n\n")
        f.write("请根据实验记录填写下表：\n")
        f.write("+--------+----------------+----------------+--------------------------------------------------+\n")
        f.write("| 元件   | 2a (V)          | 2b (V)          | 轨迹形状及说明                                   |\n")
        f.write("+--------+----------------+----------------+--------------------------------------------------+\n")
        f.write("| 电阻 R | ______________ | ______________ | 直线（斜率代表电阻值）                            |\n")
        f.write("| 电感 L | ______________ | ______________ | 椭圆（顺时针旋转，电压超前电流）                  |\n")
        f.write("| 电容 C | ______________ | ______________ | 椭圆（逆时针旋转，电流超前电压）                  |\n")
        f.write("+--------+----------------+----------------+--------------------------------------------------+\n\n")
        f.write("（请将X-Y波形截图插入报告图5.5位置，并标出a、b值）\n\n")

        # ---- 实验结论总结 ----
        f.write("【实验结论总结】\n")
        f.write("-" * 60 + "\n")
        f.write("1. 电阻元件的阻抗模不随频率变化，保持恒定（约2kΩ），电压与电流同相位。\n")
        f.write("2. 电感元件的阻抗模随频率线性增加（XL = 2πfL），电压超前电流90°。\n")
        f.write("3. 电容元件的阻抗模随频率增加而减小（XC = 1/(2πfC)），电流超前电压90°。\n")
        f.write("4. 在X-Y模式下，电阻表现为直线，电感和电容表现为椭圆，旋转方向不同，验证了相位关系。\n\n")

        f.write("注：以上带下划线“__________”的部分，请根据实际实验测量结果填写。\n")
        f.write("=" * 80 + "\n")

    print(f"实验报告文本已生成：{REPORT_FILE}")

# ================== 主程序 ==================
def main():
    data_path = SCRIPT_DIR / "data.csv"
    if not data_path.exists():
        print(f"错误：未找到 {data_path} 文件，请确保 data.csv 与 main.py 在同一目录下。")
        # 创建一个示例data.csv提示用户
        sample = """f_kHz,R_Ubc_mV,L_Ubc_mV,C_Ubc_mV
10,10.9,125,134
20,10.3,61.7,245
30,10.5,43.9,380
40,10.3,32.6,486
50,10.4,25.0,600
"""
        with open(data_path, 'w', encoding='utf-8') as f:
            f.write(sample)
        print(f"已创建示例 data.csv，请将您的实测数据填入后重新运行程序。")
        return

    df_raw = load_data(data_path)
    # 检查是否有缺失值
    if df_raw[['R_Ubc_mV', 'L_Ubc_mV', 'C_Ubc_mV']].isnull().values.any():
        print("警告：CSV文件中存在缺失数据（NaN），请补全后再运行。")
        return

    df_calc = calc_impedance(df_raw)
    print_and_save_table(df_calc)
    plot_impedance_curves(df_calc)
    generate_report(df_calc)

if __name__ == "__main__":
    main()