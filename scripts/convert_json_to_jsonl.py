import json
import os

# === 输入输出路径配置 ===
INPUT_PATH = "data/original_data.json"          # 原始 JSON 文件（数组格式）
OUTPUT_PATH = "data/disassembly.jsonl"          # 目标 JSONL 文件路径
DEFAULT_GROUP = "Task-1"                        # 默认任务分组名称（如需自定义可改）

# === 确保 data 目录存在 ===
os.makedirs("data", exist_ok=True)

# === 读取原始 JSON 数组 ===
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# === 写入为 JSONL 格式，并补全缺失字段 ===
with open(OUTPUT_PATH, "w", encoding="utf-8") as f_out:
    count = 0
    for item in data:
        item["group"] = item.get("group", DEFAULT_GROUP)  # 补充 group 字段
        json_line = json.dumps(item, ensure_ascii=False)
        f_out.write(json_line + "\n")
        count += 1

print(f"✅ 成功将 {count} 条记录转换为 JSONL 格式，并写入 {OUTPUT_PATH}")
