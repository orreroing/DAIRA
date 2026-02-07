import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# 1. Paths and Settings
# Update this filename to match your actual file
input_file_path = r'D:\sysu\Data\Effectiveness_Table.xlsx' 
output_dir = r'D:\sysu\Data\result_image'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_image_path = os.path.join(output_dir, 'Trace_Tool_Final_Chart_WideBars.png')
output_pdf_path = os.path.join(output_dir, 'Trace_Tool_Final_Chart_WideBars.pdf')

# 2. Data Loading and Processing
print("Loading data...")

try:
    df = pd.read_excel(input_file_path)
except Exception as e:
    print(f"Excel load failed, trying CSV mode: {e}")
    df = pd.read_csv(input_file_path, engine='python')

# Map your actual Excel headers to standard names here
# Change the keys (left side) if your excel still has Chinese headers
column_mapping = {
    'difficulty_col': 'difficulty', # Or 'difficulty.1' based on logic below
    'model_col': '模型名称 (Model)',   # Update this to match your Excel header
    'resolved_col': '解决标记 (Bool)' # Update this to match your Excel header
}

# Auto-detect difficulty column if standard name is missing
diff_col = None
possible_diff_cols = ['difficulty', 'difficulty.1']
for col in possible_diff_cols:
    if col in df.columns:
        diff_col = col
        break

if diff_col is None:
    # Fallback: search for a column containing specific time strings
    for col in df.columns:
        if df[col].astype(str).str.contains('15 min').any():
            diff_col = col
            break

if diff_col is None:
    raise ValueError("Difficulty column not found, please check data.")

# Normalize difficulty values
def merge_difficulty(val):
    if val in ['1-4 hours', '>4 hours']:
        return '> 1 hour'
    return val

df['Merged_Difficulty'] = df[diff_col].apply(merge_difficulty)

# Aggregate data
# Note: Ensure the column names in groupby match your Excel file headers
try:
    merged_stats = df.groupby([column_mapping['model_col'], 'Merged_Difficulty'])[column_mapping['resolved_col']].mean().reset_index()
    merged_stats = merged_stats.rename(columns={
        column_mapping['resolved_col']: 'Resolution Rate', 
        column_mapping['model_col']: 'Model'
    })
except KeyError as e:
    print(f"Error: Column not found. Please update 'column_mapping' in the script. Missing: {e}")
    raise

# 3. Plotting Configuration
print("Plotting...")

# Define x-axis order
order = ['<15 min fix', '15 min - 1 hour', '> 1 hour']

# Sort models: Non-DAIRA first, DAIRA last (to appear on the right)
all_models = merged_stats['Model'].unique().tolist()
trace_models = sorted([m for m in all_models if "DAIRA" in m])
other_models = sorted([m for m in all_models if "DAIRA" not in m])
hue_order = other_models + trace_models 

# Color Configuration
# Baseline models: Cool colors
other_palette_colors = ['#708a94', '#97c3a3', '#246092', '#adb9bd', '#bcc8c2']
# Highlight models (DAIRA): Warm colors
trace_colors = ["#f0a69c", "#e57a6d"] 

palette = {}
for i, m in enumerate(other_models):
    palette[m] = other_palette_colors[i % len(other_palette_colors)]
for i, m in enumerate(trace_models):
    palette[m] = trace_colors[i % len(trace_colors)]

# 4. Generate Plot
plt.rcParams['font.family'] = 'sans-serif' 
plt.figure(figsize=(18, 7))
sns.set_theme(style="white", font_scale=1.1) 
plt.grid(axis='y', linestyle='-', alpha=0.3, color='#d3d3d3', zorder=0)

ax = sns.barplot(
    data=merged_stats,
    x="Merged_Difficulty",
    y="Resolution Rate",
    hue="Model",
    hue_order=hue_order, 
    order=order,
    palette=palette,
    edgecolor="#333333",
    linewidth=1.0,
    alpha=0.9,
    width=0.82,
    zorder=3
)

# 5. Annotation and Styling
plt.ylabel('Resolved(%)', fontsize=18, fontweight='bold')
plt.xlabel('')
plt.ylim(0, 1.1) 
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))

# Tick fonts
plt.xticks(fontsize=18, fontweight='bold')
plt.yticks(fontsize=14, fontweight='bold')

# Annotation Logic
max_scores = merged_stats.groupby('Merged_Difficulty')['Resolution Rate'].max()

for i, container in enumerate(ax.containers):
    if i >= len(hue_order): break
    model_name = hue_order[i]
    # Identify if this is the specific tool to highlight
    is_trace_tool = "DAIRA + Gemini 3 Flash Preview" in model_name 
    
    for j, bar in enumerate(container):
        height = bar.get_height()
        if np.isnan(height) or height <= 0: continue
        
        cat_name = order[j]
        max_val = max_scores.get(cat_name, 0)
        
        # Annotate if: It is the DAIRA tool OR it is the highest score in the group
        if is_trace_tool or abs(height - max_val) < 1e-6:
            x = bar.get_x() + bar.get_width() / 2
            ax.annotate(f'{height:.1%}', 
                        (x, height), 
                        ha='center', va='bottom', 
                        fontsize=16, 
                        fontweight='bold',
                        xytext=(0, 3), 
                        textcoords='offset points')

plt.legend(loc='upper right', bbox_to_anchor=(0.98, 0.99), ncol=1, fontsize=12)
plt.tight_layout()

# 6. Save and Show
plt.savefig(output_image_path, dpi=300, bbox_inches='tight')
plt.savefig(output_pdf_path, dpi=300, bbox_inches='tight')
print(f"Chart saved to: {output_image_path} and {output_pdf_path}")
plt.show()