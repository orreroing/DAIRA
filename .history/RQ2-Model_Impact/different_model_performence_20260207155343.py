import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns

# 1. Settings and Paths
save_dir = r"D:\issta26\DAIRA\result_image"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Set global theme for a clean look
sns.set_theme(style="white", font_scale=1.0)

# 2. Data Preparation
models = ['Qwen-3-Coder\nFlash', 'DeepSeek\nV3.2', 'Gemini 3\nFlash Preview']

# # Resolution Rates (%)
# rates_swe = [50.20, 65.40, 73.60]
# rates_trace = [50.60, 74.20, 79.40]

# # Average Costs ($)
# costs_swe = [0.0732, 0.1039, 0.2695]
# costs_trace = [0.0505, 0.1143, 0.2392]
import pandas as pd

# 1. 读取数据
df = pd.read_excel(r'RQ2-Model_Impact\Different_model.xlsx')

# 2. 辅助函数：从 '模型' 列中分离出 Agent 和 Model 名称
def extract_agent_model(full_name):
    parts = full_name.split(' + ')
    if len(parts) == 2:
        return parts[0], parts[1]
    return full_name, '' # 处理异常情况

# 3. 应用函数创建新的 'Agent' 和 'Model' 列
df[['Agent', 'Model']] = df['模型'].apply(lambda x: pd.Series(extract_agent_model(x)))

# 4. 分组计算：
# - '解决标记 (Bool)' 的均值即为解决率，乘以 100 转换为百分比
# - '$ Cost' 的均值即为平均成本
summary = df.groupby(['Agent', 'Model']).agg({
    '解决标记 (Bool)': lambda x: x.mean() * 100,
    '$ Cost': 'mean'
}).reset_index()

# 5. 定义模型顺序（确保与您绘图时的 x 轴顺序一致）
model_order = ['Qwen-3-Coder Flash', 'DeepSeek V3.2', 'Gemini 3 Flash Preview']

# 6. 将 Model 列设为有序分类类型，并按指定顺序排序
summary['Model'] = pd.Categorical(summary['Model'], categories=model_order, ordered=True)
summary = summary.sort_values('Model')

# 7. 分别提取 SWE-agent 和 DAIRA (trace) 的数据
swe_data = summary[summary['Agent'] == 'SWE-agent']
daira_data = summary[summary['Agent'] == 'DAIRA']

# 8. 生成最终的列表数据结构
# Resolution Rates (%)
rates_swe = [round(x, 2) for x in swe_data['解决标记 (Bool)'].tolist()]
rates_trace = [round(x, 2) for x in daira_data['解决标记 (Bool)'].tolist()]

# Average Costs ($)
costs_swe = [round(x, 4) for x in swe_data['$ Cost'].tolist()]
costs_trace = [round(x, 4) for x in daira_data['$ Cost'].tolist()]

# 9. 打印结果以供直接复制使用
print("# Resolution Rates (%)")
print(f"rates_swe = {rates_swe}")
print(f"rates_trace = {rates_trace}")
print("\n# Average Costs ($)")
print(f"costs_swe = {costs_swe}")
print(f"costs_trace = {costs_trace}")

x = np.arange(len(models))
width = 0.35

# Color Configuration (Academic Morandi Style)
COLOR_GRAY_BLUE = '#708a94'  # Baseline (SWE-agent)
COLOR_CORAL = '#e57a6d'      # DAIRA (Resolution Rate Highlight)
COLOR_SAGE = '#97c3a3'       # DAIRA (Cost Highlight)
COLOR_UP = '#c0392b'         # Annotation: Increase (Deep Red)
COLOR_DOWN = '#2d8a4e'       # Annotation: Decrease (Deep Green)

# 3. Core Function: Labeling
def autolabel_with_change(ax, rects_base, rects_ours, is_cost=False):
    """
    Annotates bars with values and calculates the percentage change 
    between the base model and our model.
    """
    # Annotate the "Our Model" (second) bars with value + % change
    for rect_b, rect_o in zip(rects_base, rects_ours):
        height_b = rect_b.get_height()
        height_o = rect_o.get_height()
        
        # Format the value label
        label_text = f'{height_o:.4f}' if is_cost else f'{height_o:.1f}%'
        
        # Calculate percentage change
        change_pct = ((height_o - height_b) / height_b) * 100
        
        # Determine arrow symbol and color
        if change_pct > 0.0001: 
            symbol, diff_text, color_diff = "↑", f"+{change_pct:.1f}%", COLOR_UP
        elif change_pct < -0.0001:
            symbol, diff_text, color_diff = "↓", f"{change_pct:.1f}%", COLOR_DOWN
        else:
            symbol, diff_text, color_diff = "", "0.0%", "#555555"

        # Draw value
        ax.annotate(label_text,
                    xy=(rect_o.get_x() + rect_o.get_width() / 2, height_o),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # Draw percentage change (stacked above value)
        ax.annotate(f"{symbol} {diff_text}",
                    xy=(rect_o.get_x() + rect_o.get_width() / 2, height_o),
                    xytext=(0, 16), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, color=color_diff, fontweight='bold')

    # Annotate the "Base Model" (first) bars with value only
    for rect in rects_base:
        height = rect.get_height()
        label = f'{height:.4f}' if is_cost else f'{height:.1f}%'
        ax.annotate(label, 
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, color='#7f8c8d')

# 4. Plot 1: Resolution Rate
plt.figure(figsize=(7, 4), dpi=300)
ax1 = plt.gca()

rects1 = ax1.bar(x - width/2, rates_swe, width, label='SWE-agent', color=COLOR_GRAY_BLUE, edgecolor='#333333', linewidth=0.8)
rects2 = ax1.bar(x + width/2, rates_trace, width, label='DAIRA', color=COLOR_CORAL, edgecolor='#333333', linewidth=0.8)

ax1.set_ylabel('Resolved (%)', fontsize=12, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(models, fontsize=12, fontweight='bold')
ax1.set_ylim(0, 115) # Adjusted limit to make room for annotations
ax1.grid(axis='y', linestyle='-', alpha=0.2)
ax1.legend(loc='upper left', frameon=True, fontsize=10)

autolabel_with_change(ax1, rects1, rects2, is_cost=False)

plt.tight_layout()
out_path1 = os.path.join(save_dir, "Figure9(a).pdf")
plt.savefig(out_path1, bbox_inches='tight')
print(f"Saved: {out_path1}")
plt.show()

# 5. Plot 2: Average Cost
plt.figure(figsize=(7, 4), dpi=300)
ax2 = plt.gca()

rects3 = ax2.bar(x - width/2, costs_swe, width, label='SWE-agent', color=COLOR_GRAY_BLUE, edgecolor='#333333', linewidth=0.8)
rects4 = ax2.bar(x + width/2, costs_trace, width, label='DAIRA', color=COLOR_SAGE, edgecolor='#333333', linewidth=0.8)

ax2.set_ylabel('Avg. Cost ($)', fontsize=12, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(models, fontsize=12, fontweight='bold')
ax2.set_ylim(0, max(costs_swe + costs_trace) * 1.5) # Adjusted limit
ax2.grid(axis='y', linestyle='-', alpha=0.2)
ax2.legend(loc='upper left', frameon=True, fontsize=10)

autolabel_with_change(ax2, rects3, rects4, is_cost=True)

plt.tight_layout()
out_path2 = os.path.join(save_dir, "Figure9(b).pdf")
plt.savefig(out_path2, bbox_inches='tight')
print(f"Saved: {out_path2}")
plt.show()