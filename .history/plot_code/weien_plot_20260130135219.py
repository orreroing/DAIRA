import pandas as pd
import matplotlib.pyplot as plt
# 确保安装了 venn 库: pip install venn
from venn import venn 

# ==========================================
# 1. 数据加载
# ==========================================
# 请确保路径正确
file_path = r"D:\sysu\Data\各种方法的效果总表.xlsx" 
print(f"正在读取文件: {file_path} ...")

df = pd.read_excel(file_path)

# 【修改点】更新排除逻辑：排除 DAIRA 的 DeepSeek 版本 (原 Trace_tool+DeepSeek)
# 如果不排除它，它可能会挤掉 Mini-SWE (Gemini) 导致 Top 5 中出现两个 DAIRA
df_filtered = df[df['模型名称 (Model)'] != 'DAIRA + DeepSeek V3.2'].copy()

# ==========================================
# 2. 筛选 Top 5
# ==========================================
model_stats = df_filtered.groupby('模型名称 (Model)')['解决标记 (Bool)'].agg(['sum', 'count'])
model_stats['rate'] = model_stats['sum'] / model_stats['count']
top_5_models = model_stats.sort_values(by='rate', ascending=False).head(5).index.tolist()

print("Top 5 模型列表:")
for i, m in enumerate(top_5_models, 1):
    print(f"{i}. {m}")

# ==========================================
# 3. 构建数据
# ==========================================
venn_data = {}
for model_name in top_5_models:
    solved_tasks = set(
        df_filtered[
            (df_filtered['模型名称 (Model)'] == model_name) & 
            (df_filtered['解决标记 (Bool)'] == 1)
        ]['测试实例ID (Instance ID)']
    )
    
    short_name = model_name
    
    # 【修改点】更新 DAIRA 的命名逻辑
    if 'DAIRA' in model_name: 
        short_name = "DAIRA(Gemini 3 Flash Preview)"
    elif 'OpenHands' in model_name: 
        short_name = "OpenHandsClaude Opus 4.5)"
    elif 'Live-SWE' in model_name: 
        short_name = "Live-SWE-agent(Gemini 3 Pro Preview)"
    # 保留原有的 Mini-SWE 区分逻辑
    elif 'Mini-SWE' in model_name and 'Claude' in model_name: 
        short_name = "Mini-SWE-agent(Claude 4.5 Opus)"
    elif 'Mini-SWE' in model_name and 'Gemini' in model_name: 
        short_name = "Mini-SWE-agent(Gemini 3 Pro Preview)"

    venn_data[short_name] = solved_tasks

# ==========================================
# 4. 绘制超大画布韦恩图
# ==========================================
plt.rcParams.update({
    'legend.fontsize': 14,   
    'figure.titlesize': 24,
    'font.size': 16          
})

print("正在生成大尺寸韦恩图...")

# 绘制韦恩图
venn(
    venn_data, 
    alpha=0.5,
    fontsize=16,       
    legend_loc="upper right" ,
)

plt.tight_layout()

# 保存图片
output_file = "venn_diagram_large.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"已生成大图: {output_file}")

plt.show()