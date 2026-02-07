import json
import os

def parse_trajectory_direct_action(data):
    """
    解析轨迹数据，直接读取原数据中的 'action' 字段。
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

def process_directory(directory_path):
    """
    批量处理指定文件夹下的所有 .traj 文件
    """
    # 检查文件夹是否存在
    if not os.path.exists(directory_path):
        print(f"错误: 找不到文件夹 '{directory_path}'")
        return

    # 获取文件夹内所有以 .traj 结尾的文件
    files = [f for f in os.listdir(directory_path) if f.endswith('.traj')]
    
    if not files:
        print(f"在 '{directory_path}' 中未找到 .traj 文件。")
        return

    print(f"--- 开始处理，共找到 {len(files)} 个文件 ---")

    success_count = 0
    
    for filename in files:
        input_path = os.path.join(directory_path, filename)
        
        # 自动生成输出文件名：将 .traj 替换为 _steps.json
        # 例如: pylint-6528.traj -> pylint-6528_steps.json
        output_filename = filename.replace('.traj', '_steps.json')
        output_path = os.path.join(directory_path, output_filename)

        try:
            # 读取文件
            with open(input_path, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
            
            # 解析数据
            parsed_data = parse_trajectory_direct_action(input_data)
            
            # 写入新文件
            with open(output_path, 'w', encoding='utf-8') as f_out:
                json.dump(parsed_data, f_out, ensure_ascii=False, indent=4)
            
            print(f"[成功] {filename} -> {output_filename} (包含 {len(parsed_data)} 步)")
            success_count += 1
            
        except json.JSONDecodeError:
            print(f"[失败] 文件 '{filename}' JSON 格式错误，已跳过。")
        except Exception as e:
            print(f"[失败] 处理 '{filename}' 时发生未知错误: {e}")

    print(f"--- 处理结束: 成功 {success_count} / 总数 {len(files)} ---")

if __name__ == "__main__":
    # --- 配置区域 ---
    # 请在这里输入你要批量处理的文件夹路径
    target_folder = r'D:\issta26\DAIRA\traj\DAIRA__deepseekV3.2\astropy__astropy-7166'
    
    # 运行批量处理
    process_directory(target_folder)