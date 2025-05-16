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
- Login with neo4j / password123
- Try the following Cypher queries:





