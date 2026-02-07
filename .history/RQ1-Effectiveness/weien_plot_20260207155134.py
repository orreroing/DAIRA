import pandas as pd
import matplotlib.pyplot as plt
import os
# Ensure venn is installed: pip install venn
from venn import venn 

# ==========================================
# 1. Data Loading and Settings
# ==========================================
# Update this path to your actual file location
file_path = r"RQ1-Effectiveness\SOTA_Methods.xlsx" 
output_dir = r"result_image"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print(f"Loading file: {file_path} ...")

try:
    df = pd.read_excel(file_path)
except Exception as e:
    print(f"Excel load failed, trying CSV: {e}")
    df = pd.read_csv(file_path, engine='python')

# --- COLUMN MAPPING ---
# Updated based on your screenshot
col_method = 'Method'       # Column A
col_id = 'Instance ID'      # Column B
col_bool = 'Bool'           # Column D

# Verify columns exist
if not all(col in df.columns for col in [col_method, col_id, col_bool]):
    raise ValueError(f"Columns not found. Expected: {[col_method, col_id, col_bool]}")

# ==========================================
# 2. Filter and Select Top 5
# ==========================================
# Logic: Exclude DAIRA + DeepSeek version to avoid having two DAIRA versions in Top 5
# Note: Ensure the string matches exactly what is in your Excel 'Method' column
df_filtered = df[df[col_method] != 'DAIRA + DeepSeek V3.2'].copy()

# Calculate success rate
model_stats = df_filtered.groupby(col_method)[col_bool].agg(['sum', 'count'])
model_stats['rate'] = model_stats['sum'] / model_stats['count']

# Get Top 5 models by success rate
top_5_models = model_stats.sort_values(by='rate', ascending=False).head(5).index.tolist()

print("Top 5 Models Selected:")
for i, m in enumerate(top_5_models, 1):
    print(f"{i}. {m}")

# ==========================================
# 3. Build Venn Data Sets
# ==========================================
venn_data = {}

for model_name in top_5_models:
    # Get set of Instance IDs where Bool == 1 (Resolved)
    solved_tasks = set(
        df_filtered[
            (df_filtered[col_method] == model_name) & 
            (df_filtered[col_bool] == 1)
        ][col_id]
    )
    
    short_name = model_name
    
    # Renaming Logic (Updated for clarity)
    if 'DAIRA' in model_name: 
        short_name = "DAIRA (Gemini 3 Flash Preview)"
    elif 'OpenHands' in model_name: 
        # Fixed typo: added missing parenthesis
        short_name = "OpenHands (Claude Opus 4.5)" 
    elif 'Live-SWE' in model_name: 
        short_name = "Live-SWE-agent (Gemini 3 Pro Preview)"
    elif 'Mini-SWE' in model_name and 'Claude' in model_name: 
        short_name = "Mini-SWE-agent (Claude 4.5 Opus)"
    elif 'Mini-SWE' in model_name and 'Gemini' in model_name: 
        short_name = "Mini-SWE-agent (Gemini 3 Pro Preview)"

    venn_data[short_name] = solved_tasks

# ==========================================
# 4. Generate Venn Diagram
# ==========================================
print("Generating Venn diagram...")

# Update plot settings for better visibility
plt.rcParams.update({
    'legend.fontsize': 12,   
    'figure.titlesize': 20,
    'font.size': 14          
})

# Create the plot
# Note: 'venn' function automatically creates a figure
fig = venn(
    venn_data, 
    alpha=0.5,
    fontsize=14,       
    legend_loc="upper right"
)

# Save the figure

output_pdf = os.path.join(output_dir, "Figure5.pdf")


plt.savefig(output_pdf, dpi=300, bbox_inches='tight')

plt.show()