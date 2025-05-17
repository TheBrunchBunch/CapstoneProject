import json
from py2neo import Graph, Node
from collections import defaultdict

class DisassemblyGraph:
    def __init__(self, data_path, neo4j_host, neo4j_user, neo4j_password,
                 mysql_host=None, mysql_user=None, mysql_password=None, mysql_database=None):
        self.data_path = data_path
        self.graph = Graph(neo4j_host, auth=(neo4j_user, neo4j_password))
        self.data_list = []  # store all raw records

    def read_nodes(self):
        """
        Load JSONL data into memory and extract entity sets & triples.
        """
        tools = []
        components = []
        actions = []
        sources = []
        relations = []

        with open(self.data_path, 'r', encoding='utf-8') as file:
            for count, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON decode error at line {count}: {e}")
                    continue

                tool = data.get('tool')
                action = data.get('action')
                component = data.get('component')
                source = data.get('source')
                group = data.get('group')

                if tool: tools.append(tool)
                if action: actions.append(action)
                if component: components.append(component)
                if source: sources.append(source)

                if tool and action and component:
                    relations.append([tool, action, component])
                if group and action:
                    self.data_list.append(data)

                print(f"✅ Processed line {count}")

        return set(tools), set(components), set(actions), set(sources), relations

    def create_node(self, label, nodes):
        """
        Create nodes with label and name.
        """
        for name in nodes:
            node = Node(label, name=name)
            self.graph.merge(node, label, "name")

    def create_relationship(self, start_label, end_label, pairs, rel_type, rel_name):
        """
        Create relationships using Cypher.
        """
        for s, e in pairs:
            query = f"""
            MATCH (a:{start_label} {{name: $s}}), (b:{end_label} {{name: $e}})
            MERGE (a)-[:{rel_type} {{name: $rel_name}}]->(b)
            """
            try:
                self.graph.run(query, s=s, e=e, rel_name=rel_name)
            except Exception as ex:
                print(f"❌ Failed to link {s} -[{rel_type}]-> {e}: {ex}")

    def create_graphrels(self, tools, components, actions, sources, relations):
        """
        Create all main semantic relationships.
        """
        print("🔗 Tool → Action → Component")
        self.create_relationship("Tool", "Action", [[t, a] for t, a, _ in relations], "USED_TO", "Tool used for")
        self.create_relationship("Action", "Component", [[a, c] for _, a, c in relations], "APPLIED_ON", "Action applied on")

        print("📚 Action → Source")
        self.create_relationship("Action", "Source", zip([d['action'] for d in self.data_list],
                                                         [d['source'] for d in self.data_list]), "REQUIRES_SOURCE", "Action source")

    def create_task_nodes(self):
        """
        Create Task nodes (group) and link to actions.
        """
        grouped = defaultdict(list)
        for d in self.data_list:
            grouped[d["group"]].append(d["action"])

        for group, actions in grouped.items():
            self.graph.run("MERGE (:Task {name: $name})", name=group)
            for action in actions:
                query = """
                MATCH (t:Task {name: $g}), (a:Action {name: $a})
                MERGE (t)-[:INCLUDES]->(a)
                """
                self.graph.run(query, g=group, a=action)

    def create_sequence_edges(self):
        """
        Link actions in same group with :NEXT relationships.
        """
        grouped = defaultdict(list)
        for d in self.data_list:
            grouped[d["group"]].append(d["action"])

        for group, action_list in grouped.items():
            for i in range(len(action_list) - 1):
                a1 = action_list[i]
                a2 = action_list[i + 1]
                query = """
                MATCH (a1:Action {name: $a1}), (a2:Action {name: $a2})
                MERGE (a1)-[:NEXT]->(a2)
                """
                self.graph.run(query, a1=a1, a2=a2)

    def query_disassembly_process(self, tool, component):
        """
        Optional: query all actions from tool to component.
        """
        query = """
        MATCH (t:Tool)-[:USED_TO]->(a:Action)-[:APPLIED_ON]->(c:Component)
        WHERE t.name = $tool AND c.name = $component
        RETURN a.name AS action
        """
        return self.graph.run(query, tool=tool, component=component).data()
