#!/usr/bin/env python3
import os
import textwrap

from openai import OpenAI

def get_system_prompt_for_workflow_analysis() -> str:
    """
    Build the system prompt used for DAIRA trace summarization.
    """
    return textwrap.dedent("""
    Role: You are a senior Python developer and code debugging expert, skilled at analyzing trace logs to understand code execution logic.

    Task: Your task is to analyze three inputs I provide: the target code, the name of the function being traced, and the corresponding trace log for that function.

    Based on these inputs, you must generate a clear execution workflow analysis report.

    [INPUT DATA]

    Target Code (<target-file>): (Paste your target code here)

    Function to Trace (<function_to_trace>): (Enter the name of the function you traced here)

    Trace Log (<trace_log>): (Paste your trace log here)

    [ANALYSIS REPORT]

    **Important Format Requirement:** You must generate the analysis as a visual, step-by-step execution trace diagram that represents the recursive or nested call structure. **Do NOT use a simple list or summary for the main analysis.**

    Your report must precisely follow this structure:

    1.  **Initial Representation:** Clearly state the initial expression, input, or internal representation being processed (e.g., `Internal Representation: ...`).
    2.  **Top-Level Call:** Show the main, top-level function call that begins the execution (e.g., `Printer._print(...)`).
    3.  **Execution Tree:**
        * Use **ASCII/Unicode tree characters** (like `│`, `├`, `└`, `─`) to create an indented, nested flow diagram representing the call stack and logic flow.
        * **Number each step** sequentially (e.g., `(1)`, `(2)`, `(3)`).
        * **Label each step** with the function name or action being taken (e.g., `(1) Dispatch: ...`, `(2) Handle_NodeA: ...`).
        * Clearly show **recursive calls** or dispatches to sub-functions, and how they are nested within their parent.
        * Indicate what is **returned** from each key sub-call (e.g., `... Returns "Sub-Result"`).
        * Show how results from sub-calls are **combined or processed** by their parent call (e.g., `(7) Combine_Results: ...`).
    4.  **Final Output:** Conclude with a distinct line showing the **Final Output** of the entire process (e.g., `Final Output: "A - B*A"`).
    5.  **Key Function Analysis: Identify and list the key function calls from the log that played a decisive role in the execution. Please ignore trivial helper functions (like __init__, genexpr, or basic type printing) and focus only on those essential for achieving the target functionality.Function Details: For each key function you list, please provide the following information:
            a.Function and Location: The function name and its file path/line number extracted from the log.(It must be strictly ensured to be consistent with the tracking logs.)
            b.Functional Boundary: Based on the code and log context,describe the function's core responsibility in this code
            c.Role in this Workflow: Explain the function's specific role and purpose within the overall workflow.
    6.  **Introduce the entire workflow process
    """)

def get_user_content_for_workflow_analysis(problem_input: str) -> str:
    """
    Wrap the collected target file and trace log in a user prompt.
    """
    return textwrap.dedent(f"""
    Please analyze the full workflow captured below. 

    ---
    {problem_input}
    ---
    """)



def call_llm_for_analysis(problem_statement: str) :
    """
    Call the LLM API to summarize the trace into a workflow report.
    """
    
    system_prompt = get_system_prompt_for_workflow_analysis()
    user_content = get_user_content_for_workflow_analysis(problem_statement)
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = "https://api.deepseek.com"

    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            model="deepseek-chat",  
            max_tokens=6000,
        )
        return chat_completion.choices[0].message.content

    except Exception as e:
        error_message = str(e).lower()
        if ("context length" in error_message or 
            "context_length_exceeded" in error_message or 
            "too large" in error_message or
            "maximum context length" in error_message):
            
            # Return a concise, user-facing hint for context overflow.
            return (
            "\n❌ [LLM Analysis Error - Context Window Exceeded]\n"
            "==============================================================\n"
            "Error: The total length of the trace log and code exceeds the model's maximum context window (tokens).\n"
            "This may be because the function being tracked is too complex, generating a massive amount of logs.\n"
            "\n"
            "Proposed solution:\n"
            " 1. (Preferred) Reduce your trace_depth appropriately\n"
            " 2. Check if your --module_prefix is too broad, causing it to trace too many unrelated library calls.\n"
            " 3. Try to trace a more specific, deeper-level function.\n"
            "==============================================================\n"
            )
        
        return (
            f"❌ [LLM analysis error]\n"
            f"The API rejected the request. Possible causes: invalid format or parameters.\n"
            f"Original error: {e}"
        )
        

def handle_trace_log(problem_input_string:str):
    if '```text\n```' in problem_input_string:
        return (
            "\n=================== LLM workflow analyse ==================\n"
            "There is no corresponding trace log in <trace_log>; tracing was unsuccessful. "
            "Please choose the top-level function you called directly, or trace the non-built-in wrapper "
            "around a Python built-in function.\n"
            "=============================================================="
        )
    else:
        analysis_content = call_llm_for_analysis(problem_input_string)
        if analysis_content:
            return (
                "\n=================== LLM workflow analyse ==================\n"
                f"{analysis_content}\n"
                "=============================================================="
            )
        return "\n❌ LLM analysis failed."



    
    
    
