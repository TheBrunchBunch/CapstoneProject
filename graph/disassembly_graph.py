import os
import json
from py2neo import Graph, Node

class DisassemblyGraph:
    def __init__(self, data_path, neo4j_host, neo4j_user, neo4j_password,
                 mysql_host=None, mysql_user=None, mysql_password=None, mysql_database=None):
        self.data_path = data_path
        self.graph = Graph(neo4j_host, auth=(neo4j_user, neo4j_password))

    def read_nodes(self):
        """
        Read entities and relationships from the input JSON file.
        Returns sets of tools, components, actions, times, sources, and all triplets.
        """
        tools = []
        components = []
        actions = []
        times = []
        sources = []
        relations = []  # (tool, action, component) triples

        with open(self.data_path, 'r', encoding='utf-8') as file:
            for count, line in enumerate(file, 1):
                data_json = json.loads(line)
                tool = data_json.get('tool')
                component = data_json.get('component')
                action = data_json.get('action')
                time = data_json.get('time')
                source = data_json.get('source')

                if tool: tools.append(tool)
                if component: components.append(component)
                if action: actions.append(action)
                if time: times.append(time)
                if source: sources.append(source)

                if tool and action and component:
                    relations.append([tool, action, component])

                print(f"✅ Processed line {count}")

        return set(tools), set(components), set(actions), set(times), set(sources), relations

    def create_node(self, label, nodes):
        """
        Create nodes in Neo4j with a given label (Tool, Action, Component, etc.).
        Uses MERGE to avoid duplicates.
        """
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.graph.merge(node, label, "name")

    def create_graphrels(self, tools, components, actions, times, sources, relations):
        """
        Create all semantic relationships in the graph:
        Tool→Action, Action→Component, Action→Time, Action→Source.
        """
        print("🔗 Creating Tool → Action → Component relationships...")
        self.create_relationship('Tool', 'Action', relations, 'USED_TO', 'Tool used for')
        self.create_relationship('Action', 'Component', relations, 'APPLIED_ON', 'Action applied on')

        print("⏱️ Creating Action → Time relationships...")
        self.create_relationship('Action', 'Time', zip(actions, times), 'ESTIMATED_TIME', 'Disassembly time')

        print("📚 Creating Action → Source relationships...")
        self.create_relationship('Action', 'Source', zip(actions, sources), 'REQUIRES_SOURCE', 'Action source')

    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        """
        Create relationships between two node types based on input edges.
        Uses parameterized Cypher query to avoid injection issues.
        """
        for edge in edges:
            p = edge[0]
            q = edge[1]
            query = f"""
            MATCH (p:{start_node} {{name: $p_name}}), (q:{end_node} {{name: $q_name}})
            CREATE (p)-[:{rel_type} {{name: $rel_name}}]->(q)
            """
            try:
                self.graph.run(query, p_name=p, q_name=q, rel_name=rel_name)
            except Exception as e:
                print(f"⚠️ Failed to create relationship: {p} -[{rel_type}]-> {q} | Reason: {e}")

    def query_disassembly_process(self, tool, component):
        """
        Query disassembly steps: find actions linking a specific tool and component.
        """
        query = """
        MATCH (t:Tool)-[:USED_TO]->(a:Action)-[:APPLIED_ON]->(c:Component)
        WHERE t.name = $tool AND c.name = $component
        RETURN a.name AS action, c.name AS component
        """
        result = self.graph.run(query, tool=tool, component=component)
        return result.data()
