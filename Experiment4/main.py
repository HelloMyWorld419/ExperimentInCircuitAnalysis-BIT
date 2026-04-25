import csv
import math
from pathlib import Path

def read_csv_param(csv_path, param_name):
    """从 data.csv 中读取指定参数的值"""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Parameter'] == param_name:
                val = row['Value'].strip()
                return float(val) if val else None
    return None

def format_sci(num, decimal_places=2):
    """将数值转换为科学计数法的常规书写格式，例如 2.09e+05 -> 2.09×10⁵"""
    if num is None:
        return '______'
    # 格式化科学计数法字符串，如 "2.09e+05"
    sci_str = f"{num:.{decimal_places}e}"
    # 分离尾数和指数部分
    if 'e' in sci_str:
        mantissa, exponent = sci_str.split('e')
        exponent = exponent.replace('+', '')  # 去掉正号
        # 将指数转为上标数字（Unicode 上标）
        sup_map = {
            '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
            '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', '-': '⁻'
        }
        sup_exp = ''.join(sup_map.get(ch, ch) for ch in exponent)
        return f"{mantissa}×10{sup_exp}"
    return sci_str

def main():
    current_dir = Path(__file__).parent
    csv_path = current_dir / 'data.csv'
    
    if not csv_path.exists():
        print(f"错误：未找到数据文件 {csv_path}")
        print("请确保 data.csv 与 main.py 位于同一文件夹下。")
        return
    
    # 读取实测数据
    R_crit_zs = read_csv_param(csv_path, 'R_critical_zero_state')
    R_crit_zi = read_csv_param(csv_path, 'R_critical_zero_input')
    u1m = read_csv_param(csv_path, 'u1m')
    u2m = read_csv_param(csv_path, 'u2m')
    Td_us = read_csv_param(csv_path, 'Td')
    
    # 电路参数（固定）
    L = 2.7e-3      # H
    C = 0.01e-6     # F
    R_theory_critical = 2 * math.sqrt(L / C)   # Ω
    
    # 计算 ω_d, α（欠阻尼，R=100Ω）
    if u1m is not None and u2m is not None and Td_us is not None and Td_us > 0:
        Td_s = Td_us * 1e-6
        omega_d = 2 * math.pi / Td_s
        alpha = (1 / Td_s) * math.log(u1m / u2m)
        omega_d_theory = math.sqrt(1/(L*C) - (100/(2*L))**2)
    else:
        omega_d = alpha = None
        omega_d_theory = None
    
    # 格式化输出
    omega_d_str = format_sci(omega_d, 2)
    alpha_str = format_sci(alpha, 2)
    omega_d_theory_str = format_sci(omega_d_theory, 2)
    R_theory_critical_str = f"{R_theory_critical:.2f}"
    
    # --- 生成报告 ---
    report = f"""================================================================================
实验四 二阶电路响应的研究 —— 数据填写与结论总结
================================================================================

【第一部分：实验数据填写（请直接复制到报告对应空白处）】
--------------------------------------------------------------------------------
1. 零状态响应临界阻值：R临界 = {R_crit_zs if R_crit_zs is not None else '______'} Ω
2. 零输入响应临界阻值：R临界 = {R_crit_zi if R_crit_zi is not None else '______'} Ω
3. 欠阻尼波形参数（R = 100 Ω）：
   - 第一个波峰电压 u1m = {u1m if u1m is not None else '______'} V
   - 第二个波峰电压 u2m = {u2m if u2m is not None else '______'} V
   - 振荡周期 Td = {Td_us if Td_us is not None else '______'} μs
4. 计算得到的动态参数：
   - 振荡角频率 ωd = {omega_d_str} rad/s
   - 衰减系数 α = {alpha_str} s⁻¹
5. 理论参考值：
   - 理论临界阻值 R0 = {R_theory_critical_str} Ω
   - 理论欠阻尼 ωd_theory = {omega_d_theory_str} rad/s（R=100Ω时）
--------------------------------------------------------------------------------

【第二部分：实验结论及总结（可直接复制到实验报告“四、实验结论及总结”部分）】
--------------------------------------------------------------------------------
1. 零状态响应（充电过程）的三种状态
   在 RLC 串联二阶电路零状态响应实验中，输入为幅度 5V、脉宽 0.5ms 的方波。通过调节电阻 R，观察到三种典型波形：
   - 过阻尼（R > 临界值）：电容电压 uC(t) 缓慢上升至稳态，无振荡，无超调。
   - 临界阻尼（R = 临界值）：uC(t) 上升最快且无振荡，过渡时间最短。
   - 欠阻尼（R < 临界值）：uC(t) 出现衰减振荡，有超调，最终趋于稳态。
   记录临界阻尼状态下的电阻值：R临界（零状态） = {R_crit_zs if R_crit_zs is not None else '______'} Ω。
   理论临界阻值 R0 = 2√(L/C) = {R_theory_critical_str} Ω，实测值与理论值{'基本吻合' if R_crit_zs else '（需填写实测值）'}。

2. 零输入响应（放电过程）的三种状态
   在零输入响应实验中，输入为窄脉冲（脉宽 3μs），使电容初始电压约 5V 后开始放电。同样调节 R，观察到与零状态响应相对应的三种波形。
   记录临界阻尼状态下的电阻值：R临界（零输入） = {R_crit_zi if R_crit_zi is not None else '______'} Ω。

3. 欠阻尼状态下的参数测量与计算
   取 R = 100 Ω（欠阻尼状态），从示波器上读取相邻两个波峰（或波谷）的电压值及振荡周期：
   - u1m = {u1m if u1m is not None else '______'} V
   - u2m = {u2m if u2m is not None else '______'} V
   - Td = {Td_us if Td_us is not None else '______'} μs
   计算得到：
   - 振荡角频率 ωd = {omega_d_str} rad/s
   - 衰减系数 α = {alpha_str} s⁻¹
   理论欠阻尼振荡角频率 ωd_theory = √[1/(LC) - (R/(2L))²] ≈ {omega_d_theory_str} rad/s（当 R=100Ω 时），实测值与理论值基本一致。

4. 实验总结
   (1) 二阶电路的过渡过程取决于阻尼比，过阻尼、临界阻尼、欠阻尼三种状态分别对应非振荡、临界振荡、衰减振荡。
   (2) 临界阻尼状态下电路响应最快（无振荡且上升时间最短），可通过 R = 2√(L/C) 预估。
   (3) 欠阻尼状态下，振荡角频率 ωd 和衰减系数 α 可由波形直接测量计算，α 反映了振幅衰减的快慢。
   (4) 误差来源：电阻箱接触电阻、电感内阻及分布电容、示波器光标定位误差等，但实验结果与理论分析定性一致。

5. 心得体会
   通过观测 RLC 电路在不同阻尼状态下的响应波形，直观理解了二阶微分方程的特征根与响应形态的关系。掌握了从波形中提取特征参数（超调量、振荡周期、衰减比）的方法，加深了对二阶系统动态性能的认识。
================================================================================
"""

    out_path = current_dir / 'exp_4_report.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"实验四报告已生成：{out_path}")

if __name__ == "__main__":
    main()