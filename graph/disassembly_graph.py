import json
import hashlib
from py2neo import Graph, Node
from collections import defaultdict

class DisassemblyGraph:
    def __init__(self, data_path, neo4j_host, neo4j_user, neo4j_password,
                 mysql_host=None, mysql_user=None, mysql_password=None, mysql_database=None,
                 strict_group=False):  # ✅ 新增配置项，兼容有无 group 字段
        self.data_path = data_path
        self.graph = Graph(neo4j_host, auth=(neo4j_user, neo4j_password))
        self.data_list = []  # Stores all raw JSON records
        self.strict_group = strict_group  # 控制是否依赖 group 字段
    
    def read_nodes(self):
        tools, components, actions, sources, relations = [], [], [], [], []
        source_action_counter = defaultdict(lambda: defaultdict(int))  # source → action → count

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
                source = data.get('source') or "Unknown Source"  # ✅ 缺失 source 时使用默认值

                if not action:
                    print(f"⚠️ Missing action at line {count}, skipping.")
                    continue

                # ✅ 构建唯一的 Action 名称
                if self.strict_group:
                    if group:
                        unique_action = f"{group}::{action}"
                    else:
                        print(f"⚠️ Line {count} missing group in strict mode, skipping.")
                        continue
                else:
                    # 为每个 (source, action) 添加编号 + 哈希前缀
                    source_hash = hashlib.md5(source.encode()).hexdigest()[:6]
                    source_action_counter[source][action] += 1
                    suffix = source_action_counter[source][action]
                    unique_action = f"{source_hash}_{action}_{suffix}"

                data["unique_action"] = unique_action
                self.data_list.append(data)
                actions.append(unique_action)

                if tool:
                    tools.append(tool)
                if component:
                    components.append(component)
                if source:
                    sources.append(source)

                if tool and action and component:
                    relations.append([tool, unique_action, component])

                print(f"✅ Processed line {count}")

        return set(tools), set(components), set(actions), set(sources), relations, self.data_list


    def create_node(self, label, nodes):
        for name in nodes:
            node = Node(label, name=name)
            self.graph.merge(node, label, "name")

    def create_action_nodes(self):
        for d in self.data_list:
            node = Node("Action", name=d["unique_action"])
            self.graph.merge(node, "Action", "name")

    def create_relationship(self, start_label, end_label, pairs, rel_type, rel_name):
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
        print("🔗 Creating Tool → Action → Component relationships...")
        self.create_relationship("Tool", "Action", [[t, a] for t, a, _ in relations], "USED_TO", "Tool used for")
        self.create_relationship("Action", "Component", [[a, c] for _, a, c in relations], "APPLIED_ON", "Action applied on")

        print("📚 Creating Action → Source relationships...")
        self.create_relationship("Action", "Source",
            [[d["unique_action"], d["source"]] for d in self.data_list if d.get("source")],
            "REQUIRES_SOURCE", "Action source")

    def create_task_nodes(self):
        grouped = defaultdict(list)
        for d in self.data_list:
            if self.strict_group and "group" in d:
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
        grouped = defaultdict(list)
        for d in self.data_list:
            if self.strict_group and "group" in d:
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
        query = """
        MATCH (t:Tool)-[:USED_TO]->(a:Action)-[:APPLIED_ON]->(c:Component)
        WHERE t.name = $tool AND c.name = $component
        RETURN a.name AS action
        """
        return self.graph.run(query, tool=tool, component=component).data()