# CapstoneProject

## Project Structure
CapstoneProject/
├── data/
│   └── disassembly.jsonl        # Entity triples (tool-action-component-source)
├── docker-compose.yml           # Neo4j service definition
├── graph/
│   └── disassembly_graph.py     # Graph construction logic
├── config/
│   └── config.py                # Reads Neo4j credentials from .env
├── main.py                      # Execution entry
├── .env                         # Contains Neo4j URI/user/password (ignored)
└── requirements.txt             # Python dependencies

## Part3: Neo4j Setup & Knowledge Graph Construction
This project uses Neo4j to construct a disassembly knowledge graph from structured JSONL data.

### 1. Prerequisites
- Docker + Docker Compose installed  
- Python 3.8+  

### 2. Start Neo4j via Docker
1. Set up virtual environment and install packages from requirements.txt
2. In the project root directory, run: docker compose up -d
3. Run graph builder: python main.py

### 3. Visualize in Neo4j Browser:
- Visit http://localhost:7474
- Login with neo4j / password123 (you can change to your own config)
- Try the following Cypher queries:
1. Retrieve all nodes (and their relationships)：MATCH (n) RETURN n LIMIT 100;
2. Find all Tool → Action → Component paths: 
MATCH (t:Tool)-[:USED_TO]->(a:Action)-[:APPLIED_ON]->(c:Component)
RETURN t.name   AS Tool,
     a.name   AS Action,
     c.name   AS Component
LIMIT 50;
3. Find all Action → Source paths：
MATCH (a:Action)-[:REQUIRES_SOURCE]->(s:Source)
RETURN a.name   AS Action,
       s.name   AS Source
LIMIT 50;
4. For a given tool, list which components it disassembles: 
MATCH (t:Tool {name: "Screwdriver"})
      -[:USED_TO]->(a:Action)
      -[:APPLIED_ON]->(c:Component)
RETURN a.name   AS Action,
       c.name   AS Component;
5. For a given component, list which actions disassemble it: 
MATCH (a:Action)
      -[:APPLIED_ON]->(c:Component {name: "screw"})
RETURN a.name   AS Action,
       c.name   AS Component;
6. Find the source literature for a specific action: 
MATCH (a:Action {name: "UNSCREW"})
      -[:REQUIRES_SOURCE]->(s:Source)
RETURN s.name   AS Source;
