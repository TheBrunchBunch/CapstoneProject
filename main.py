from graph.disassembly_graph import DisassemblyGraph
from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

# Initialize handler
handler = DisassemblyGraph(
    data_path="data/disassembly.jsonl",
    neo4j_host=NEO4J_URI,
    neo4j_user=NEO4J_USER,
    neo4j_password=NEO4J_PASSWORD,
    strict_group=False  # ✅ 设置为 False，即使数据没有 group 也能运行
)

print("🔍 Initializing disassembly graph builder...")

# Load and extract data
tools, components, actions, sources, relations, data_list = handler.read_nodes()

# Create nodes
handler.create_node("Tool", tools)
handler.create_node("Component", components)
handler.create_node("Source", sources)
handler.create_node("Action", actions)

# Create semantic relationships
handler.create_graphrels(tools, components, actions, sources, relations)

# Create task and :INCLUDES links
#handler.create_task_nodes()

# Create :NEXT sequential edges
#handler.create_sequence_edges()

print("✅ Disassembly knowledge graph built successfully!")