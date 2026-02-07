import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns

# ==========================================
# 0. 设置保存路径
# ==========================================
save_dir = r"D:\sysu\Data\result_image"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# 设置全局样式，使其更接近参考图的清爽感
sns.set_theme(style="white", font_scale=1.0)

# ==========================================
# 1. 数据准备
# ==========================================
models = ['Qwen-3-Coder\nFlash', 'DeepSeek\nV3.2', 'Gemini 3\nFlash Preview']
rates_swe = [50.20, 65.40, 73.60]
rates_trace = [50.60, 74.20, 79.40]
costs_swe = [0.0732, 0.1039, 0.2695]
costs_trace = [0.0505, 0.1143, 0.2392]

x = np.arange(len(models))
width = 0.35

# 定义学术莫兰迪色系
COLOR_GRAY_BLUE = '#708a94'  # SWE-agent (基准)
COLOR_CORAL = '#e57a6d'      # TraceTool (成功率图重点色)
COLOR_SAGE = '#97c3a3'       # TraceTool (成本图重点色)
COLOR_UP = '#c0392b'         # 标注：涨 (深红)
COLOR_DOWN = '#2d8a4e'       # 标注：跌 (深绿)

# ==========================================
# 核心函数：绘制标签
# ==========================================
def autolabel_with_change(ax, rects_base, rects_ours, is_cost=False):
    for rect_b, rect_o in zip(rects_base, rects_ours):
        height_b = rect_b.get_height()
        height_o = rect_o.get_height()
        label_text = f'{height_o:.4f}' if is_cost else f'{height_o:.1f}%'
        change_pct = ((height_o - height_b) / height_b) * 100
        
        if change_pct > 0.0001: 
            symbol, diff_text, color_diff = "↑", f"+{change_pct:.1f}%", COLOR_UP
        elif change_pct < -0.0001:
            symbol, diff_text, color_diff = "↓", f"{change_pct:.1f}%", COLOR_DOWN
        else:
            symbol, diff_text, color_diff = "", "0.0%", "#555555"

        # 绘制数值
        ax.annotate(label_text,
                    xy=(rect_o.get_x() + rect_o.get_width() / 2, height_o),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        # 绘制幅度
        ax.annotate(f"{symbol} {diff_text}",
                    xy=(rect_o.get_x() + rect_o.get_width() / 2, height_o),
                    xytext=(0, 16), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, color=color_diff, fontweight='bold')

    for rect in rects_base:
        height = rect.get_height()
        label = f'{height:.4f}' if is_cost else f'{height:.1f}%'
        ax.annotate(label, xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, color='#7f8c8d')

# ==========================================
# 图一：Resolve Rate
# ==========================================
plt.figure(figsize=(7, 4), dpi=300)
ax1 = plt.gca()

# 使用灰蓝 vs 珊瑚红
rects1 = ax1.bar(x - width/2, rates_swe, width, label='SWE-agent', color=COLOR_GRAY_BLUE, edgecolor='#333333', linewidth=0.8)
rects2 = ax1.bar(x + width/2, rates_trace, width, label='DAIRA', color=COLOR_CORAL, edgecolor='#333333', linewidth=0.8)

ax1.set_ylabel('Resolved(%)', fontsize=12, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(models,fontsize=12, fontweight='bold')
ax1.set_ylim(0, 110)
ax1.grid(axis='y', linestyle='-', alpha=0.2) # 浅色实线网格
ax1.legend(loc='upper left', frameon=True, fontsize=10)

autolabel_with_change(ax1, rects1, rects2, is_cost=False)
plt.tight_layout()
plt.savefig(os.path.join(save_dir, "resolution_rate_comparison.pdf"), bbox_inches='tight')
plt.show()

# ==========================================
# 图二：Avg. Cost
# ==========================================
plt.figure(figsize=(7, 4), dpi=300)
ax2 = plt.gca()

# 使用灰蓝 vs 鼠尾草绿
rects3 = ax2.bar(x - width/2, costs_swe, width, label='SWE-agent', color=COLOR_GRAY_BLUE, edgecolor='#333333', linewidth=0.8)
rects4 = ax2.bar(x + width/2, costs_trace, width, label='DAIRA', color=COLOR_SAGE, edgecolor='#333333', linewidth=0.8)

ax2.set_ylabel('Avg. Cost ($)', fontsize=12, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(models,fontsize=12, fontweight='bold')
ax2.set_ylim(0, max(costs_swe + costs_trace) * 1.4)
ax2.grid(axis='y', linestyle='-', alpha=0.2)
ax2.legend(loc='upper left', frameon=True, fontsize=10)

autolabel_with_change(ax2, rects3, rects4, is_cost=True)
plt.tight_layout()
plt.savefig(os.path.join(save_dir, "avg_cost_comparison.pdf"), bbox_inches='tight')
plt.show()