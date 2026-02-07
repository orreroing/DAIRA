import json
import os

def parse_trajectory_direct_action(data):
    """
    解析轨迹数据，直接读取原数据中的 'action' 字段。
    (此函数保持不变)
    """
    history = data.get("history", [])
    
    # 根据之前的上下文，通常跳过前两项 (System Prompt 和 User Prompt)
    start_index = 2 
    step_count = 1

    actions_data = []

    for i in range(start_index, len(history), 2):
        # 1. 获取 Assistant 消息
        assistant_msg = history[i]
        
        # 确保有对应的 Tool 消息 (防止越界)
        if i + 1 >= len(history):
            break
            
        # 2. 获取 Tool 消息
        tool_msg = history[i+1]

        # --- A. 提取 Thought ---
        thought = assistant_msg.get("thought", "").strip()

        # --- B. 直接提取 Action 字段 ---
        raw_action = assistant_msg.get("action", "No Action")

        # --- C. 提取 Observation ---
        content = tool_msg.get("content", "")
        observation = ""
        
        if isinstance(content, str):
            observation = content
        elif isinstance(content, list):
            texts = [item.get("text", "") for item in content if item.get("type") == "text"]
            observation = "\n".join(texts)

        # --- D. 构建当前步骤的字典对象 ---
        step_item = {
            "step": step_count,
            "thought": thought,
            "action": raw_action,
            "observation": observation.strip()
        }
        
        actions_data.append(step_item)
        step_count += 1

    return actions_data

def process_directory_recursive(root_folder):
    """
    递归遍历指定文件夹（包含所有子文件夹）下的所有 .traj 文件并处理
    """
    # 检查文件夹是否存在
    if not os.path.exists(root_folder):
        print(f"错误: 找不到文件夹 '{root_folder}'")
        return

    print(f"--- 开始在 '{root_folder}' 下递归扫描 ---")

    total_files_count = 0
    success_count = 0
    
    # os.walk 会遍历目录树：current_root是当前正在遍历的文件夹路径
    for current_root, dirs, files in os.walk(root_folder):
        
        # 筛选当前文件夹下的 .traj 文件
        traj_files = [f for f in files if f.endswith('.traj')]
        
        for filename in traj_files:
            total_files_count += 1
            
            # 获取完整输入路径
            input_path = os.path.join(current_root, filename)
            
            # 自动生成输出文件名，保存在同级目录下
            output_filename = filename.replace('.traj', '_steps.json')
            output_path = os.path.join(current_root, output_filename)

            try:
                # 读取文件
                with open(input_path, 'r', encoding='utf-8') as f:
                    input_data = json.load(f)
                
                # 解析数据
                parsed_data = parse_trajectory_direct_action(input_data)
                
                # 写入新文件
                with open(output_path, 'w', encoding='utf-8') as f_out:
                    json.dump(parsed_data, f_out, ensure_ascii=False, indent=4)
                
                print(f"[成功] ...\\{os.path.basename(current_root)}\\{filename} -> 生成 {len(parsed_data)} 步")
                success_count += 1
                
            except json.JSONDecodeError:
                print(f"[失败] 文件 '{filename}' JSON 格式错误，已跳过。")
            except Exception as e:
                print(f"[失败] 处理 '{filename}' 时发生未知错误: {e}")

    if total_files_count == 0:
        print("未找到任何 .traj 文件。")
    else:
        print(f"--- 处理结束: 成功 {success_count} / 总计发现 {total_files_count} 个文件 ---")

if __name__ == "__main__":
    # --- 配置区域 ---
    # 这里输入你的父级文件夹路径 (就是截图中包含很多 astropy... 子文件夹的那个目录)
    target_folder = r'D:\issta26\DAIRA\traj\DAIRA__gemini-3-flash-preview'
    
    # 运行递归批量处理
    process_directory_recursive(target_folder)