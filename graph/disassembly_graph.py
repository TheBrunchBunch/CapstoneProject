import json
from py2neo import Graph, Node
from collections import defaultdict

class DisassemblyGraph:
    def __init__(self, data_path, neo4j_host, neo4j_user, neo4j_password,
                 mysql_host=None, mysql_user=None, mysql_password=None, mysql_database=None):
        self.data_path = data_path
        self.graph = Graph(neo4j_host, auth=(neo4j_user, neo4j_password))
        self.data_list = []  # Stores all raw JSON records with group + action combined

    def read_nodes(self):
        """
        Load data from a JSONL file.
        Generate sets of tools, components, actions, sources, and relationships.
        Each Action is task-specific: group::action
        """
        tools, components, actions, sources, relations = [], [], [], [], []

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

                group = data.get('group')
                tool = data.get('tool')
                action = data.get('action')
                component = data.get('component')
                source = data.get('source')

                if group and action:
                    data["unique_action"] = f"{group}::{action}"
                    self.data_list.append(data)
                    actions.append(f"{group}::{action}")

                if tool: tools.append(tool)
                if component: components.append(component)
                if source: sources.append(source)
                if tool and action and component:
                    relations.append([tool, f"{group}::{action}", component])

                print(f"✅ Processed line {count}")

        return set(tools), set(components), set(actions), set(sources), relations, self.data_list

    def create_node(self, label, nodes):
        """
        Create basic nodes (Tool, Component, Source) using MERGE to avoid duplication.
        """
        for name in nodes:
            node = Node(label, name=name)
            self.graph.merge(node, label, "name")

    def create_action_nodes(self):
        """
        Create Action nodes. Each Action node is uniquely scoped within a group.
        """
        for d in self.data_list:
            node = Node("Action", name=d["unique_action"])
            self.graph.merge(node, "Action", "name")

    def create_relationship(self, start_label, end_label, pairs, rel_type, rel_name):
        """
        Create relationships based on label and edge type.
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
        Build main semantic links: Tool→Action, Action→Component, Action→Source.
        """
        print("🔗 Creating Tool → Action → Component relationships...")
        self.create_relationship("Tool", "Action", [[t, a] for t, a, _ in relations], "USED_TO", "Tool used for")
        self.create_relationship("Action", "Component", [[a, c] for _, a, c in relations], "APPLIED_ON", "Action applied on")

        print("📚 Creating Action → Source relationships...")
        self.create_relationship("Action", "Source",
            [[d["unique_action"], d["source"]] for d in self.data_list if d.get("source")],
            "REQUIRES_SOURCE", "Action source")

    def create_task_nodes(self):
        """
        Create Task nodes and link each to its sequence of Actions.
        """
        grouped = defaultdict(list)
        for d in self.data_list:
            grouped[d["group"]].append(d["unique_action"])

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
        Add :NEXT links between steps (Actions) in order for each task.
        """
        grouped = defaultdict(list)
        for d in self.data_list:
            grouped[d["group"]].append(d["unique_action"])

        for group, actions in grouped.items():
            for i in range(len(actions) - 1):
                a1 = actions[i]
                a2 = actions[i + 1]
                query = """
                MATCH (a1:Action {name: $a1}), (a2:Action {name: $a2})
                MERGE (a1)-[:NEXT]->(a2)
                """
                self.graph.run(query, a1=a1, a2=a2)

    def query_disassembly_process(self, tool, component):
        """
        Query the actions used between a specific tool and component.
        """
        query = """
        MATCH (t:Tool)-[:USED_TO]->(a:Action)-[:APPLIED_ON]->(c:Component)
        WHERE t.name = $tool AND c.name = $component
        RETURN a.name AS action
        """
        return self.graph.run(query, tool=tool, component=component).data()