import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns

# Settings
save_dir = r"D:\issta26\DAIRA\result_image"
if not os.path.exists(save_dir):
    try:
        os.makedirs(save_dir)
    except OSError:
        pass

sns.set_theme(style="white", font_scale=1.0)

# Data Preparation
# Please ensure the filename matches your local file
df = pd.read_excel(r"D:\issta26\DAIRA\different_model.xlsx")

def parse_model_string(s):
    if " + " in s:
        parts = s.split(" + ")
        return parts[0], parts[1]
    return "Unknown", s

df[['Agent', 'Base_Model']] = df['模型'].apply(lambda x: pd.Series(parse_model_string(x)))

grouped = df.groupby(['Base_Model', 'Agent']).agg({
    '解决标记 (Bool)': 'mean',
    '$ Cost': 'mean'
}).reset_index()

grouped['Resolution Rate'] = grouped['解决标记 (Bool)'] * 100

model_mapping = {
    'Qwen-3-Coder Flash': 'Qwen-3-Coder\nFlash',
    'DeepSeek V3.2': 'DeepSeek\nV3.2',
    'Gemini 3 Flash Preview': 'Gemini 3\nFlash Preview'
}

pivot_rates = grouped.pivot(index='Base_Model', columns='Agent', values='Resolution Rate')
pivot_costs = grouped.pivot(index='Base_Model', columns='Agent', values='$ Cost')

ordered_models = ['Qwen-3-Coder Flash', 'DeepSeek V3.2', 'Gemini 3 Flash Preview']
pivot_rates = pivot_rates.reindex(ordered_models)
pivot_costs = pivot_costs.reindex(ordered_models)

models_display = [model_mapping.get(m, m) for m in ordered_models]
rates_swe = pivot_rates['SWE-agent'].tolist()
rates_trace = pivot_rates['DAIRA'].tolist()
costs_swe = pivot_costs['SWE-agent'].tolist()
costs_trace = pivot_costs['DAIRA'].tolist()

x = np.arange(len(models_display))
width = 0.35

# Color Configuration
COLOR_GRAY_BLUE = '#708a94'   # SWE-agent
COLOR_CORAL = '#e57a6d'       # DAIRA (Resolution Rate)
COLOR_SAGE = '#97c3a3'        # DAIRA (Cost)
COLOR_UP = '#c0392b'          # Increase
COLOR_DOWN = '#2d8a4e'        # Decrease

# Helper Function for Labeling
def autolabel_with_change(ax, rects_base, rects_ours, is_cost=False):
    for rect_b, rect_o in zip(rects_base, rects_ours):
        height_b = rect_b.get_height()
        height_o = rect_o.get_height()
        
        label_text = f'{height_o:.4f}' if is_cost else f'{height_o:.1f}%'
        
        # Calculate percentage change
        change_pct = ((height_o - height_b) / height_b) * 100
        
        if change_pct > 0.0001: 
            symbol, diff_text, color_diff = "↑", f"+{change_pct:.1f}%", COLOR_UP
        elif change_pct < -0.0001:
            symbol, diff_text, color_diff = "↓", f"{change_pct:.1f}%", COLOR_DOWN
        else:
            symbol, diff_text, color_diff = "", "0.0%", "#555555"

        # Annotation for value
        ax.annotate(label_text,
                    xy=(rect_o.get_x() + rect_o.get_width() / 2, height_o),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # Annotation for percentage change
        ax.annotate(f"{symbol} {diff_text}",
                    xy=(rect_o.get_x() + rect_o.get_width() / 2, height_o),
                    xytext=(0, 16), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, color=color_diff, fontweight='bold')

    # Annotation for base bars
    for rect in rects_base:
        height = rect.get_height()
        label = f'{height:.4f}' if is_cost else f'{height:.1f}%'
        ax.annotate(label, 
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, color='#7f8c8d')

# Plot 1: Resolution Rate
plt.figure(figsize=(7, 4), dpi=300)
ax1 = plt.gca()

rects1 = ax1.bar(x - width/2, rates_swe, width, label='SWE-agent', color=COLOR_GRAY_BLUE, edgecolor='#333333', linewidth=0.8)
rects2 = ax1.bar(x + width/2, rates_trace, width, label='DAIRA', color=COLOR_CORAL, edgecolor='#333333', linewidth=0.8)

ax1.set_ylabel('Resolved (%)', fontsize=12, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(models_display, fontsize=12, fontweight='bold')
ax1.set_ylim(0, 115)
ax1.grid(axis='y', linestyle='-', alpha=0.2)
ax1.legend(loc='upper left', frameon=True, fontsize=10)

autolabel_with_change(ax1, rects1, rects2, is_cost=False)

plt.tight_layout()
out_path1 = os.path.join(save_dir, "Figure9(a).pdf")
plt.savefig(out_path1, bbox_inches='tight')
plt.show()

# Plot 2: Average Cost
plt.figure(figsize=(7, 4), dpi=300)
ax2 = plt.gca()

rects3 = ax2.bar(x - width/2, costs_swe, width, label='SWE-agent', color=COLOR_GRAY_BLUE, edgecolor='#333333', linewidth=0.8)
rects4 = ax2.bar(x + width/2, costs_trace, width, label='DAIRA', color=COLOR_SAGE, edgecolor='#333333', linewidth=0.8)

ax2.set_ylabel('Avg. Cost ($)', fontsize=12, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(models_display, fontsize=12, fontweight='bold')
ax2.set_ylim(0, max(costs_swe + costs_trace) * 1.5) 
ax2.grid(axis='y', linestyle='-', alpha=0.2)
ax2.legend(loc='upper left', frameon=True, fontsize=10)

autolabel_with_change(ax2, rects3, rects4, is_cost=True)

plt.tight_layout()
out_path2 = os.path.join(save_dir, "Figure9(b).pdf")
plt.savefig(out_path2, bbox_inches='tight')
plt.show()