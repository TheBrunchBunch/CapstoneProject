import os
import json
from py2neo import Graph, Node, Relationship
import mysql.connector

class DisassemblyGraph:
    def __init__(self, data_path, neo4j_host, neo4j_user, neo4j_password, mysql_host, mysql_user, mysql_password, mysql_database):
        self.data_path = data_path
        self.graph = Graph(neo4j_host, auth=(neo4j_user, neo4j_password)) 
        self.mysql_conn = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database
        )
        self.mysql_cursor = self.mysql_conn.cursor() 

    def read_nodes(self):
        # Read data from the JSON file and return the sets and their relationships.
        tools = []  # Tools
        components = []  # Components
        actions = []  # Actions
        times = []  # Time (seconds)
        sources = []  # Source (text or URL)
        relations = []  # Tool, action, component relationships

        with open(self.data_path, 'r') as file:
            for count, data in enumerate(file, 1):
                data_json = json.loads(data)
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

                print(f"Processed {count} lines")

        return set(tools), set(components), set(actions), set(times), set(sources), relations

    def create_node(self, label, nodes):
        # Create nodes in the Neo4j graph database 
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.graph.create(node)

    def create_graphrels(self):
        # Create relationships in the Neo4j graph database
        tools, components, actions, times, sources, relations = self.read_nodes()

        self.create_relationship('Tool', 'Action', relations, 'USED_TO', 'Tool used for')
        self.create_relationship('Action', 'Component', relations, 'APPLIED_ON', 'Action appiled on')
        self.create_relationship('Action', 'Time', zip(actions, times), 'ESTIMATED_TIME', 'disassembly time')
        self.create_relationship('Action', 'Source', zip(actions, sources), 'REQUIRES_SOURCE', 'Action source')

    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        # Create relationships by dynamically creating relationships between entities based on the data.
        for edge in edges:
            p = edge[0]
            q = edge[1]
            query = f"MATCH (p:{start_node}), (q:{end_node}) WHERE p.name='{p}' AND q.name='{q}' CREATE (p)-[rel:{rel_type}{{name:'{rel_name}'}}]->(q)"
            try:
                self.graph.run(query)
            except Exception as e:
                print(e)

    def store_to_mysql(self, tools, components, actions, relations, times, sources):
        # Store data in MySQL
        for tool in tools:
            self.mysql_cursor.execute("INSERT INTO Tools (tool_name) VALUES (%s)", (tool,))
        for component in components:
            self.mysql_cursor.execute("INSERT INTO Components (component_name) VALUES (%s)", (component,))
        for action in actions:
            self.mysql_cursor.execute("INSERT INTO DisassemblyMethods (method_name) VALUES (%s)", (action,))
        for tool, action, component in relations:
            self.mysql_cursor.execute("""
            INSERT INTO Tool_Fastener (tool_id, fastener_id) 
            SELECT t.tool_id, f.fastener_id FROM Tools t, Fasteners f 
            WHERE t.tool_name = %s AND f.fastener_name = %s
            """, (tool, component))
        for action, time in zip(actions, times):
            self.mysql_cursor.execute("""
            INSERT INTO Action_Time (action_id, estimated_time) 
            SELECT a.action_id, %s FROM Actions a WHERE a.method_name = %s
            """, (time, action))
        for action, source in zip(actions, sources):
            self.mysql_cursor.execute("""
            INSERT INTO Action_Source (action_id, source) 
            SELECT a.action_id, %s FROM Actions a WHERE a.method_name = %s
            """, (source, action))

        self.mysql_conn.commit()

    def query_disassembly_process(self, tool, component):
        # Query the disassembly process
        query = """
        MATCH (t:Tool)-[:USED_TO]->(a:Action)-[:APPLIED_ON]->(c:Component)
        WHERE t.name = $tool AND c.name = $component
        RETURN a.name AS action, c.name AS component
        """
        result = self.graph.run(query, tool=tool, component=component)
        return result

if __name__ == '__main__':
    data_path = 'data/disassembly.json'
    neo4j_host = 'bolt://localhost:7687'
    neo4j_user = 'neo4j'
    neo4j_password = 'password'
    mysql_host = 'localhost'
    mysql_user = 'root'
    mysql_password = 'password'
    mysql_database = 'disassembly_db'

    # Instantiate DisassemblyGraph class
    handler = DisassemblyGraph(data_path, neo4j_host, neo4j_user, neo4j_password, mysql_host, mysql_user, mysql_password, mysql_database)

    # Read data
    tools, components, actions, times, sources, relations = handler.read_nodes()

    # Create nodes in the disassembly graph
    handler.create_disassembly_nodes(tools, components, actions)

    # Create relationships in the disassembly process
    handler.create_graphrels()

    # Store data in MySQL
    handler.store_to_mysql(tools, components, actions, relations, times, sources)