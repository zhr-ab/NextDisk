import autogen
import os
import json
from collections import defaultdict


# ==================== 全局变量 ====================
ANALYST = None
ADVISOR = None
EDITOR = None
USER_PROXY = None
CONFIG_LIST = None


# ==================== 1. 初始化函数 ====================

def init_ollama_config(model_name: str = "deepseek-coder", base_url: str = "http://localhost:11434/v1"):
    """
    初始化 Ollama 配置
    
    参数:
        model_name: Ollama 中的模型名（如 'deepseek-coder', 'llama3', 'mistral'）
        base_url: Ollama API 地址
    
    返回:
        bool: 是否初始化成功
    """
    global CONFIG_LIST
    
    CONFIG_LIST = [
        {
            "model": model_name,
            "base_url": base_url,
            "api_key": "ollama"  # 随便填，不为空即可
        }
    ]
    
    # 测试连接
    try:
        test_agent = autogen.AssistantAgent(
            name="test",
            llm_config={"config_list": CONFIG_LIST},
            system_message="Test connection."
        )
        print(f"✅ Ollama 配置成功，模型: {model_name}")
        return True
    except Exception as e:
        print(f"❌ Ollama 连接失败: {e}")
        print("请确保 Ollama 服务已启动: ollama serve")
        return False


def init_agents():
    """
    初始化所有 Agent（数据分析师、市场顾问、报告主编、用户代理）
    """
    global ANALYST, ADVISOR, EDITOR, USER_PROXY
    
    # 确保配置已初始化
    if CONFIG_LIST is None:
        raise ValueError("请先调用 init_ollama_config() 初始化配置")
    
    # 创建工作目录
    os.makedirs("./workspace", exist_ok=True)
    os.makedirs("./workspace/reports", exist_ok=True)
    
    # 数据分析师
    ANALYST = autogen.AssistantAgent(
        name="analyst",
        llm_config={"config_list": CONFIG_LIST},
        system_message="""
        你是数据分析师，只输出客观统计数据，不做主观判断。
        你可以主动发言、质疑他人、补充信息，不必等待提问。
        用 @advisor 或 @editor 邀请他们参与讨论。
        """
    )
    
    # 市场顾问
    ADVISOR = autogen.AssistantAgent(
        name="advisor",
        llm_config={"config_list": CONFIG_LIST},
        system_message="""
        你是市场顾问，根据数据提出策略建议，可以质疑或补充数据分析师的观点。
        你可以主动发言、@analyst 要数据、@editor 协调报告。
        不必等待被点名，看到相关信息就可以参与讨论。
        """
    )
    
    # 报告主编
    EDITOR = autogen.AssistantAgent(
        name="editor",
        llm_config={"config_list": CONFIG_LIST},
        system_message="""
        你是报告主编，负责协调讨论，综合各方意见形成最终报告。
        你可以主动发言、@analyst 要数据、@advisor 要建议。
        遇到分歧时引导大家达成共识，最终产出 Markdown 报告。
        """
    )
    
    # 用户代理
    USER_PROXY = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        code_execution_config={"work_dir": "./workspace"}
    )
    
    print("✅ 所有 Agent 初始化成功")


def init_all(model_name: str = "deepseek-coder"):
    """
    一键初始化所有配置和 Agent
    
    参数:
        model_name: Ollama 中的模型名
    
    返回:
        bool: 是否初始化成功
    """
    if not init_ollama_config(model_name):
        return False
    init_agents()
    return True


# ==================== 2. 自由讨论函数 ====================

def start_free_discussion(csv_file: str = "sales_data.csv"):
    """
    启动自由讨论流程
    """
    global USER_PROXY, ANALYST  #
    
    if USER_PROXY is None or ANALYST is None:
        raise ValueError("请先调用 init_all() 初始化")
    
    # 确保 CSV 文件存在
    csv_path = os.path.join("./workspace", csv_file)
    if not os.path.exists(csv_path):
        sample_data = """product,sales,growth
A,120000,0.15
B,85000,-0.08
C,95000,0.05
D,60000,0.02"""
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(sample_data)
        print(f"📄 示例 CSV 文件已创建: {csv_path}")
    
    # 初始任务
    initial_message = f"""
请读取 workspace/{csv_file}，分析各产品总销售额、增长率。
然后你们三位（@analyst @advisor @editor）自由讨论如何形成最终报告。
讨论过程中可以互相 @ 邀请发言，直到达成共识并生成报告。
报告保存到 workspace/reports/final_report.md
"""
    
    print("\n🚀 启动自由讨论...")
    USER_PROXY.initiate_chat(ANALYST, message=initial_message)  # 👈 用全局变量 USER_PROXY
    
    # 多轮延续讨论
    USER_PROXY.initiate_chat(
        ANALYST,
        message="@advisor 请基于当前数据提出你的市场策略，@editor 请准备综合框架，我们继续讨论。"
    )
    
    USER_PROXY.initiate_chat(
        EDITOR,
        message="请综合我们之前的讨论，生成最终 Markdown 报告，保存到 workspace/reports/final_report.md，并告诉我文件路径。"
    )
    
    print("✅ 自由讨论完成")
    return True


# ==================== 3. 对话时间线函数 ====================

def get_conversation_timeline(*agents):
    """
    获取所有 Agent 的对话并合并成完整时间线
    
    参数:
        agents: 一个或多个 Agent 对象
    
    返回:
        list: 对话时间线列表，每条记录包含 conversation_id, agent_name, role, content
    """
    timeline = []
    
    for agent in agents:
        if not hasattr(agent, 'chat_messages') or not agent.chat_messages:
            continue
            
        for conv_id, messages in agent.chat_messages.items():
            for msg in messages:
                timeline.append({
                    "conversation_id": conv_id,
                    "agent_name": agent.name,
                    "role": msg.get("role", "unknown"),
                    "content": msg.get("content", "")
                })
    
    # 按对话 ID 排序
    timeline.sort(key=lambda x: (x["conversation_id"], timeline.index(x)))
    
    return timeline


def print_timeline(timeline):
    """
    打印格式化的对话时间线
    
    参数:
        timeline: 对话时间线列表
    """
    print("\n" + "=" * 70)
    print("📜 完整对话时间线")
    print("=" * 70)
    
    if not timeline:
        print("暂无对话记录")
        return
    
    current_conv_id = None
    for entry in timeline:
        if entry["conversation_id"] != current_conv_id:
            current_conv_id = entry["conversation_id"]
            print(f"\n{'─' * 70}")
            print(f"🗣️  对话 ID: {current_conv_id}")
            print(f"{'─' * 70}")
        
        role_icon = "👤" if entry["role"] == "user" else "🤖"
        role_name = f"{role_icon} {entry['agent_name']} ({entry['role']})"
        
        content = entry["content"]
        if len(content) > 400:
            content = content[:400] + "\n...(内容过长，已截断)...\n" + content[-100:]
        
        print(f"\n{role_name}:\n{content}\n")


def save_timeline_json(timeline, filename: str = "conversation_log.json"):
    """
    保存对话时间线到 JSON 文件
    
    参数:
        timeline: 对话时间线列表
        filename: 保存的文件名
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)
    print(f"✅ 对话日志已保存到: {filename}")


def export_timeline_markdown(timeline, filename: str = "conversation_log.md"):
    """
    导出对话时间线到 Markdown 文件
    
    参数:
        timeline: 对话时间线列表
        filename: 保存的文件名
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# 📜 对话时间线\n\n")
        
        current_conv_id = None
        for entry in timeline:
            if entry["conversation_id"] != current_conv_id:
                current_conv_id = entry["conversation_id"]
                f.write(f"\n---\n\n## 🗣️ 对话 {current_conv_id}\n\n")
            
            role_icon = "👤" if entry["role"] == "user" else "🤖"
            f.write(f"### {role_icon} {entry['agent_name']} ({entry['role']})\n\n")
            f.write(f"{entry['content']}\n\n")
    
    print(f"✅ 对话日志已导出到: {filename}")


# ==================== 4. 报告获取函数 ====================

def get_latest_report():
    """
    获取最新生成的报告
    
    返回:
        tuple: (报告路径, 报告内容) 或 (None, 错误信息)
    """
    reports_dir = "./workspace/reports"
    
    if not os.path.exists(reports_dir):
        return None, "报告目录不存在"
    
    files = os.listdir(reports_dir)
    md_files = [f for f in files if f.endswith(".md")]
    
    if not md_files:
        return None, "报告未生成"
    
    latest_file = max(md_files, key=lambda x: os.path.getctime(os.path.join(reports_dir, x)))
    filepath = os.path.join(reports_dir, latest_file)
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    return filepath, content


def get_agent_last_message(agent):
    """
    获取指定 Agent 的最后一条消息
    
    参数:
        agent: Agent 对象
    
    返回:
        str: 最后一条消息内容，或错误信息
    """
    if not hasattr(agent, 'chat_messages') or not agent.chat_messages:
        return "该 Agent 暂无对话记录"
    
    last_conv = list(agent.chat_messages.values())[-1]
    last_msg = last_conv[-1]
    
    return f"[{last_msg['role']}]: {last_msg['content']}"


# ==================== 5. 一键运行函数 ====================

def run_full_workflow(csv_file: str = "sales_data.csv", model_name: str = "deepseek-coder"):
    """
    一键运行完整工作流程：初始化 → 自由讨论 → 获取结果
    
    参数:
        csv_file: 要分析的 CSV 文件名
        model_name: Ollama 中的模型名
    
    返回:
        dict: 包含所有结果的字典
    """
    print("\n" + "=" * 70)
    print("🚀 启动完整工作流程")
    print("=" * 70)
    
    # 1. 初始化
    if not init_all(model_name):
        return {"success": False, "error": "初始化失败"}
    
    # 2. 自由讨论
    start_free_discussion(csv_file)
    
    # 3. 获取对话时间线
    timeline = get_conversation_timeline(ANALYST, ADVISOR, EDITOR)
    print_timeline(timeline)
    save_timeline_json(timeline)
    export_timeline_markdown(timeline)
    
    # 4. 获取报告
    report_path, report_content = get_latest_report()
    
    # 5. 获取各 Agent 最后发言
    results = {
        "success": True,
        "timeline": timeline,
        "report_path": report_path,
        "report_content": report_content,
        "analyst_last_message": get_agent_last_message(ANALYST),
        "advisor_last_message": get_agent_last_message(ADVISOR),
        "editor_last_message": get_agent_last_message(EDITOR)
    }
    
    # 6. 打印总结
    print("\n" + "=" * 70)
    print("📊 工作流程完成")
    print("=" * 70)
    print(f"📜 对话记录: conversation_log.json / conversation_log.md")
    if report_path:
        print(f"📄 最终报告: {report_path}")
    else:
        print(f"❌ 报告生成失败: {report_content}")
    
    return results


# ==================== 6. 清理函数 ====================

def clear_agents():
    """
    清除所有 Agent（释放内存）
    """
    global ANALYST, ADVISOR, EDITOR, USER_PROXY, CONFIG_LIST
    ANALYST = None
    ADVISOR = None
    EDITOR = None
    USER_PROXY = None
    CONFIG_LIST = None
    print("✅ 所有 Agent 已清除")


# ==================== 主程序入口 ====================

if __name__ == "__main__":
    # 一键运行完整流程
    results = run_full_workflow(
        csv_file="sales_data.csv",
        model_name="deepseek-coder"  # 可换成 'llama3', 'mistral' 等
    )
    
    # 如果需要单独调用某个功能，可以这样：
    # init_all("llama3")
    # start_free_discussion("my_data.csv")
    # timeline = get_conversation_timeline(ANALYST, ADVISOR, EDITOR)
    # print_timeline(timeline)