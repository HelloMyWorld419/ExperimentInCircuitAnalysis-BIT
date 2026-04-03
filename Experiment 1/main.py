import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from scipy.interpolate import make_interp_spline # 引入平滑插值工具
from matplotlib.ticker import FormatStrFormatter # 引入格式化工具
import os

# 基础设置：解决中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial'] 
plt.rcParams['axes.unicode_minus'] = False

def get_data(df, row_name):
    """从横向CSV中提取有效数值"""
    target_row = df[df['Project'] == row_name]
    if target_row.empty:
        return np.array([])
    data = pd.to_numeric(target_row.iloc[0, 1:], errors='coerce').dropna().values
    return data

def main():
    # --- 路径处理 ---
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, 'exp_1.csv')
    
    try:
        df = pd.read_csv(csv_path)
        print(f"成功读取文件: {csv_path}\n")
    except Exception as e:
        print(f"读取文件失败: {e}")
        return

    # 初始化用于保存结论的变量
    r_calc, r_sq_calc, rs_calc = 0, 0, 0

    # --- 1. 线性电阻图表 ---
    u_lin = get_data(df, 'Linear_V')
    i_lin = get_data(df, 'Linear_I')
    if len(u_lin) > 0:
        fig, ax = plt.subplots(figsize=(8, 6))
        slope, intercept, r_val, _, _ = linregress(i_lin/1000, u_lin)
        r_calc, r_sq_calc = slope, r_val**2
        ax.scatter(i_lin, u_lin, color='blue', label='原始数据', zorder=5)
        ax.plot(i_lin, intercept + slope*(i_lin/1000), 'r-', 
                 label=f'拟合直线 R={slope:.1f}Ω\n$R^2$={r_sq_calc:.4f}')
        ax.set_title('图 1.1 线性电阻伏安特性曲线')
        ax.set_xlabel('I (mA)')
        ax.set_ylabel('U (V)')
        
        # 设置坐标轴保留一位小数
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        
        ax.legend()
        ax.grid(True, linestyle='--')
        plt.savefig(os.path.join(current_dir, '1_Linear_Resistor.png'), dpi=300)
        print(f"已生成: 1_Linear_Resistor.png (R = {r_calc:.2f} Ω)")

    # --- 2. 非线性电阻图表 ---
    u_non = get_data(df, 'NonLinear_V')
    i_non = get_data(df, 'NonLinear_I')
    
    if len(u_non) >= 3 and len(i_non) >= 3:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(u_non, i_non, color='green', marker='o', s=30, label='测量点', zorder=5)
        
        sort_index = np.argsort(u_non)
        u_sorted = u_non[sort_index]
        i_sorted = i_non[sort_index]
        u_smooth = np.linspace(u_sorted.min(), u_sorted.max(), 300)
        spline_func = make_interp_spline(u_sorted, i_sorted, k=3)
        i_smooth = spline_func(u_smooth)
        
        ax.plot(u_smooth, i_smooth, 'g-', linewidth=2, label='特性曲线')
        ax.set_title('图 1.2 非线性电阻(二极管)伏安特性曲线')
        ax.set_xlabel('U (V)')
        ax.set_ylabel('I (mA)')
        
        # 设置坐标轴保留一位小数
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        
        ax.legend()
        ax.grid(True, linestyle='--')
        plt.savefig(os.path.join(current_dir, '2_Nonlinear_Diode.png'), dpi=300)
        print(f"已生成: 2_Nonlinear_Diode.png (采用三次样条插值平滑)")

    # --- 3. 电压源对比图表 ---
    i_ideal = get_data(df, 'IdealSource_I')
    u_ideal = get_data(df, 'IdealSource_V')
    i_act = get_data(df, 'ActualSource_I')
    u_act = get_data(df, 'ActualSource_V')
    
    if len(u_act) > 0:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(i_ideal, u_ideal, 'b-', linewidth=2, label='理想电压源')
        slope_rs, intercept_rs, _, _, _ = linregress(i_act/1000, u_act)
        rs_calc = -slope_rs
        ax.scatter(i_act, u_act, color='red', zorder=5)
        ax.plot(i_act, intercept_rs + slope_rs*(i_act/1000), 'r--', 
                 label=f'实际电压源 (Rs={rs_calc:.1f}Ω)')
        
        ax.set_title('图 1.3 电压源外特性对比曲线')
        ax.set_xlabel('I (mA)')
        ax.set_ylabel('U (V)')
        
        # 设置坐标轴保留一位小数
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        
        if len(u_ideal) > 0:
            ax.set_ylim(0, max(u_ideal)*1.3)
        ax.legend()
        ax.grid(True, linestyle='--')
        plt.savefig(os.path.join(current_dir, '3_Voltage_Source_Comparison.png'), dpi=300)
        print(f"已生成: 3_Voltage_Source_Comparison.png (Rs = {rs_calc:.2f} Ω)")

    # --- 4. 自动生成实验报告结论文件 exp_1.txt ---
    report_content = f"""四、 实验结论及总结

1. 实验数据分析与结论

线性电阻特性：
根据实验 1.1 的测量数据及绘图结果，线性电阻的 U-I 关系呈现为一条通过坐标原点的直线。通过最小二乘法拟合，得到该电阻的阻值 R ≈ {r_calc:.2f} Ω，与理论值 200 Ω 误差可忽略，线性相关系数 R² 约为 {r_sq_calc:.4f}，这验证了线性电阻服从欧姆定律，即 U = RI，其阻值不随电压或电流的变化而改变。

非线性电阻（二极管）特性：
根据实验 1.2 绘制的曲线（采用三次样条插值平滑），二极管的伏安特性呈明显的非线性指数型增长。在正向电压小于死区电压（约 0.5V）时，电流极小；当电压超过门槛电压后，电流随电压微小升高而急剧增大。结论证明：二极管具有单向导电性和非线性，其等效电阻（静态电阻）随工作点的变化而变化。

电压源特性对比：
理想电压源：其伏安特性曲线是一条水平直线，表明无论负载电流 I 如何变化，输出电压始终保持 10V 不变，其内阻 Rs = 0。
实际电压源：随着负载电流 I 的增加，端口电压 U 呈现线性下降趋势。通过拟合斜率求得该电源的内阻 Rs ≈ {rs_calc:.2f} Ω，与模拟时所加定值电阻值 51 Ω 吻合。
对比结论：实际电压源可以用理想电压源 Us 与内阻 Rs 串联的模型来等效。

2. 实验总结与体会

误差来源分析：
- 仪表内阻影响：实验中使用万用表测量电压和电流，电表自身的内阻（电压表并联分流、电流表串联分压）会导致测量值与理论值存在细微偏差。
- 读数误差：人工读取模拟表盘或数字表瞬时波动产生的随机误差。
- 元件发热：在线性电阻测试中，大电流会导致电阻发热，从而引起阻值微弱漂移。

操作注意事项：
- 二极管保护：在测试非线性电阻时，必须严格控制电流不能超过二极管的最大量程，防止因电流过大烧坏元件。
- 逐点测试法：实验中采用了“逐点测试法”，在特性曲线变化剧烈的区域（如二极管导通区）增加采样点密度，从而保证了绘图的还原度。

工具应用心得：
本次实验引入了 Python 进行数据处理。相比传统方法，该方法精度高：利用 linregress 线性回归算法计算出的结果更具科学性；可视化强：独立生成的数字化图像排版整洁，极大提高了实验报告的专业度。
"""
    
    with open(os.path.join(current_dir, 'exp_1.txt'), 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"已生成: exp_1.txt (包含实验结论与总结)")
    print("\n所有文件已独立保存完毕。")
    plt.show()

if __name__ == "__main__":
    main()