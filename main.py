from graph.disassembly_graph import DisassemblyGraph
from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def main():
    print("Initializing disassembly graph builder...")
    handler = DisassemblyGraph(
        data_path="data/disassembly.jsonl",
        neo4j_host=NEO4J_URI,
        neo4j_user=NEO4J_USER,
        neo4j_password=NEO4J_PASSWORD,
    )

    print("Reading entity data...")
    tools, components, actions, times, sources, relations = handler.read_nodes()

    print("Creating Neo4j nodes...")
    handler.create_node("Tool", tools)
    handler.create_node("Component", components)
    handler.create_node("Action", actions)
    handler.create_node("Time", times)
    handler.create_node("Source", sources)

    print("Creating Neo4j semantic relationships...")
    handler.create_graphrels(tools, components, actions, times, sources, relations)
    print("Disassembly knowledge graph built successfully! ")

if __name__ == "__main__":
    main()
