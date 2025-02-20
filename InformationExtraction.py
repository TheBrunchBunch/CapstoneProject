import fitz  # PyMuPDF
import spacy
import re
import pandas as pd
from neo4j import GraphDatabase

# # Load PDF and extract text
pdf_path = "/Users/crescendooo/Desktop/stuff/NUS-I4/IND5005B/1-s2.0-S2212827116000998-main.pdf"
doc = fitz.open(pdf_path)
pdf_text = "\n".join(page.get_text("text") for page in doc)
# print("\n📌 **PDF 解析的前 1000 个字符**")
# print(pdf_text[:1000])


# # Load NLP model and define NER patterns
# nlp = spacy.blank("en")
# ruler = nlp.add_pipe("entity_ruler")

# # Define patterns for entity recognition
# patterns = [
#     {"label": "TOOL", "pattern": "Heat Gun"},
#     {"label": "TOOL", "pattern": "Screwdriver"},
#     {"label": "TOOL", "pattern": "Drill"},
#     {"label": "TOOL", "pattern": "Hammer"},
#     {"label": "COMPONENT", "pattern": "Adhesive"},
#     {"label": "COMPONENT", "pattern": "Battery"},
#     {"label": "COMPONENT", "pattern": "Screw"},
#     {"label": "ACTION", "pattern": "remove"},
#     {"label": "ACTION", "pattern": "unscrew"},
#     {"label": "ACTION", "pattern": "detach"},
#     {"label": "ACTION", "pattern": "disassemble"}
# ]
# ruler.add_patterns(patterns)

# # Process text with NER
# doc = nlp(pdf_text)
# entities = [(ent.text, ent.label_) for ent in doc.ents]

# # Define patterns for relationship extraction
# patterns = [
#     (r"(\w+ \w+) is used to (\w+) (\w+)", "TOOL", "ACTION", "COMPONENT"),
#     (r"(\w+) is needed to (\w+) (\w+)", "TOOL", "ACTION", "COMPONENT"),
#     (r"(\w+) can (\w+) (\w+)", "TOOL", "ACTION", "COMPONENT"),
#     (r"Use a (\w+) to (\w+) (\w+)", "TOOL", "ACTION", "COMPONENT")
# ]
# relationships = []

# # Extract relationships
# for pattern, tool_label, action_label, component_label in patterns:
#     matches = re.findall(pattern, pdf_text)
#     for match in matches:
#         tool, action, component = match
#         relationships.append((tool, action, component))

# # Convert to DataFrame
# df_entities = pd.DataFrame(entities, columns=["Entity", "Label"])
# df_relationships = pd.DataFrame(relationships, columns=["Tool", "Action", "Component"])

# # Print extracted entities
# print("\n提取的实体 (Entities Extracted)")
# print(df_entities.to_string(index=False))

# # Print extracted relationships
# print("\n提取的拆卸关系 (Extracted Disassembly Relationships)")
# print(df_relationships.to_string(index=False))

import openai
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
import g4f

def query_g4f(prompt_text):
    """使用 g4f 免费 GPT-4 提取实体和关系"""
    response = g4f.ChatCompletion.create(
        model="gpt-4",  # 可以尝试 "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt_text}]
    )
    return response  # 返回 LLM 结果



# 拆分 PDF 文本，适配 LLM 处理
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
text_chunks = text_splitter.split_text(pdf_text)

# 处理实体识别和关系抽取的 Prompt
prompt_ner_re = """
Extract detailed disassembly methods. The output should be structured in a sequential format, ensuring clarity on the tools used, components involved, and actions taken.
Ensure the output follows the structured format below.

Entities:
- TOOL: The tool or equipment used in the disassembly process (e.g., Screwdriver, Heat Gun).
- COMPONENT: The component being disassembled (e.g., Battery, Adhesive).
- ACTION: The disassembly action applied to a component using a tool (e.g., remove, unscrew, cut).
- SEQUENCE: The sequential order in which the disassembly actions should occur.

Relationships:
- (TOOL) -[:USED_TO]-> (ACTION)
- (ACTION) -[:APPLIED_ON]-> (COMPONENT)
- (ACTION_1) -[:BEFORE]-> (ACTION_2) (If the disassembly must follow a specific sequence)

Output Format:
Disassembly Process for: [OBJECT]
1. [TOOL] - [ACTION] - [COMPONENT]
2. [TOOL] - [ACTION] - [COMPONENT]
...

Example Output:
Disassembly Process for: Laptop Battery Pack
Entities:
TOOL: Screwdriver, Spudger, Hands
COMPONENT: Battery Cover, Battery Connector, Battery Module
ACTION: Unscrew, Pry, Remove

Disassembly Steps:
1. Screwdriver - Unscrew - Battery Cover
2. Spudger - Pry - Battery Connector
3. Hands - Remove - Battery Module

Text: {text}
"""
test_chunk = text_chunks[0]  # 只测试第一个文本块
response = query_g4f(prompt_ner_re.format(text=test_chunk))
print(response)

# 处理文本块并提取实体和关系
extracted_entities = set()
extracted_relationships = set()

for chunk in text_chunks:
    response = query_g4f(prompt_ner_re.format(text=chunk))
    lines = response.split("\n")

    # 解析 LLM 输出
    for line in lines:
        if line.startswith("- TOOL:"):
            extracted_entities.add((line.replace("- TOOL:", "").strip(), "TOOL"))
        elif line.startswith("- COMPONENT:"):
            extracted_entities.add((line.replace("- COMPONENT:", "").strip(), "COMPONENT"))
        elif line.startswith("- ACTION:"):
            extracted_entities.add((line.replace("- ACTION:", "").strip(), "ACTION"))
        elif line.startswith("- ("):
            match = re.findall(r"\((.*?)\) -\[:(.*?)\]-> \((.*?)\)", line)
            if match:
                extracted_relationships.add(match[0])

# 转换为 DataFrame 方便查看
df_llm_entities = pd.DataFrame(list(extracted_entities), columns=["Entity", "Label"])
df_llm_relationships = pd.DataFrame(list(extracted_relationships), columns=["Tool", "Action", "Component"])

# 显示提取的实体和关系
# Print extracted entities from LLM
print("\n LLM 提取的实体 (Entities Extracted by LLM)")
print(df_llm_entities.to_string(index=False))

# Print extracted relationships from LLM
print("\n LLM 提取的拆卸关系 (Extracted Disassembly Relationships by LLM)")
print(df_llm_relationships.to_string(index=False))




# # Neo4j connection details
# uri = "bolt://localhost:7687"  # Change this if your Neo4j instance has a different address
# neo4j_user = "neo4j"  # Default username, change if needed
# neo4j_password = "password"  # Replace with your actual password

# # Store disassembly data in Neo4j
# def store_disassembly_data(uri, user, password, relationships):
#     driver = GraphDatabase.driver(uri, auth=(user, password))

#     def add_disassembly_step(tx, tool, action, component):
#         query = """
#         MERGE (t:Tool {name: $tool})
#         MERGE (c:Component {name: $component})
#         MERGE (t)-[:USED_TO_REMOVE {action: $action}]->(c)
#         """
#         tx.run(query, tool=tool, action=action, component=component)

#     with driver.session() as session:
#         for tool, action, component in relationships:
#             session.write_transaction(add_disassembly_step, tool, action, component)

#     driver.close()
#     print("\n✅ 拆卸数据已存入 Neo4j！(Disassembly data successfully stored in Neo4j)")

# # Store extracted disassembly relationships in Neo4j
# store_disassembly_data(uri, neo4j_user, neo4j_password, relationships)
