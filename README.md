# 🔌 BIT-CircuitAnalysis-Experiments

> **电路分析基础课内实验数据处理工具 (2025-2026-2 Spring)**
>
> 本项目专为北京理工大学 (BIT) 《电路分析基础》课程设计，旨在实现实验数据的自动化处理、特性曲线拟合及结论生成，减少重复劳动，提高报告准确性。

---

## 🌟 核心功能

- **📈 多图对比可视化**：自动生成 U-I 特性曲线、功率曲线等，支持多元件数据同图对比。
- **🔢 自动化数据处理**：
  - 线性回归拟合：基于**最小二乘法**自动计算拟合曲线参数及拟合优度。
  - 定理验证：自动计算电路参数及误差分析。
- **📑 实验报告辅助**：自动生成符合要求的实验结论文本，直接辅助纸质报告填写。

---

## 📂 目录结构

```text
ExperimentInCircuitAnalysis-BIT/
├── Experiment 1/                      # 实验一：基本元件伏安特性的测绘
│   ├── main.py                        # 数据处理与绘图脚本
│   ├── exp_1.csv                      # 原始数据模板（手工填写）
│   ├── README.txt                     # 详细使用说明（实验一专有）
│   ├── 1_Linear_Resistor.png          # 生成：线性电阻伏安特性曲线
│   ├── 2_Nonlinear_Diode.png          # 生成：二极管伏安特性曲线
│   ├── 3_Voltage_Source_Comparison.png# 生成：理想/实际电压源对比曲线
│   └── exp_1.txt                      # 生成：实验结论与总结
├── Experiment 2/                      # 实验二：含源线性单口网络等效电路
│   ├── main.py                        # 数据处理与绘图脚本
│   ├── exp_2.csv                      # 原始数据模板（手工填写）
│   ├── README.txt                     # 详细使用说明（实验二专有）
│   ├── exp2_characteristic_curves.png # 生成：外特性对比曲线（图2.7）
│   └── exp_2_final_report.txt         # 生成：拟合结果与验证结论
├── .gitignore                         # 忽略生成的图片和临时文件
└── README.md                          # 项目说明文档（本文件）
```
---

## 🛠️ 基本工具包准备：

python（建议3.11），matplotlib，pandas，numpy，scipy，os

运行以下命令：
```bash
pip install pandas numpy matplotlib scipy os
```
---

## 🚀 快速上手指南

* **1. 克隆与存放**
使用 GitHub Desktop 或 Git 将仓库 Clone 到本地。确保每个实验的 .py 脚本与对应的 .csv 数据文件处于同一个子文件夹内。

* **2. 数据录入**
进入对应实验文件夹（如 Experiment 1/）。

使用 Excel 或文本编辑器打开 exp_1.csv （或data.csv）。

⚠️ 重要：严禁修改第一行（列标题）以及 Project 列中的关键词（脚本通过硬编码关键词定位数据行）。

将你在实验中记录的数据填入对应的 Point1、Point2 …… 单元格中。

示例数据已预留，请替换为自己的实测值。

部分选做内容或自动计算项可留空（参考各 CSV 文件内的注释）。

* **3.运行Python代码**
在终端中进入实验文件夹，执行：
```bash
python main.py
```

* **4.获取结果**
图片文件（.png）：已按要求绘制的特性曲线图，可直接插入实验报告。

报告文本（.txt）：包含计算出的拟合参数、误差分析和结论模板，可直接复制到纸质报告对应位置。

具体内容参照每个实验文件夹下的README.txt文件指导