# CapstoneProject

## Project Structure
CapstoneProject/
├── crawler/
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

## Part1: Web Crawler for Google Scholar and Google Search
This module is a modular web crawler and paper downloader designed to collect and process industrial disassembly–related documents using Google Search, Google Scholar, and Sci-Hub. The results are stored in MongoDB and optionally uploaded to Google Drive.

### File Overview

| File | Description |
|------|-------------|
| `google_search.py` | Uses Google Custom Search API to get URLs based on a single keyword and saves them to MongoDB. |
| `google_search_batch_run.py` | Automates batch keyword searches using `google_search.py` and updates webpage content using `web_scraping.py`. |
| `web_scraping.py` | Extracts readable text from the URLs stored in MongoDB and saves them back to the database. |
| `web_crawler.py` | Uses the `scholarly` API to fetch metadata from Google Scholar and saves it as CSV. |
| `sci_hub_pdf.py` | Downloads PDF articles from Sci-Hub using extracted URLs. |
| `main_clawer.py` | Integrates `web_crawler.py`, `sci_hub_pdf.py`, and Google Drive upload logic for a full end-to-end process. |
| `run_batch.py` | Executes multiple queries in batch mode using `main_clawer.py`. |

### Requirements

Install dependencies using:

```bash
pip install requests beautifulsoup4 pymongo scholarly
```

MongoDB must be running locally (`mongodb://localhost:27017/`).

### API Key Setup

#### 1. Google Custom Search API

For `google_search.py` and `google_search_batch_run.py`:

- Go to: https://programmablesearchengine.google.com/
- Create a search engine and get:
  - `API_KEY`: from Google Cloud Console (https://console.cloud.google.com/)
  - `SEARCH_ENGINE_ID` (also called `cx`)

Replace in `google_search.py`:

```python
API_KEY = "YOUR_API_KEY"
SEARCH_ENGINE_ID = "YOUR_SEARCH_ENGINE_ID"
```

#### 2. Google Drive API Token

Used in `main_clawer.py` for uploading PDFs:

- Visit OAuth 2.0 Playground: https://developers.google.com/oauthplayground/
- Select and authorize "Drive API v3"
- Exchange for an access token
- Replace in `main_clawer.py`:

```python
token = "YOUR_GOOGLE_DRIVE_ACCESS_TOKEN"
folder_id = "YOUR_GOOGLE_DRIVE_FOLDER_ID"
```

### Usage Instructions

#### 1. Run a Single Google Search

```bash
python google_search.py
```

Input a keyword when prompted (e.g., `bolt industry disassembly`).

#### 2. Run Batch Google Search and Scraping

```bash
python google_search_batch_run.py
```

- Performs search for a list of keywords
- Scrapes textual content from resulting webpages

#### 3. Google Scholar and Sci-Hub Download

```bash
python main_clawer.py
```

Input a query (e.g., `adhesive`) and confirm to proceed. PDFs will be downloaded and optionally uploaded to Google Drive.

#### 4. Batch Run for Google Scholar and PDF

```bash
python run_batch.py
```

Executes `main_clawer.py` for a batch of keywords.

### Output

- Web and paper metadata saved to MongoDB under:
  - `paper_database.search_results`
  - `paper_database.papers`
- Scholar results saved as CSV files under `../links/`
- PDFs saved to Google Drive (if enabled)

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

### 4. Handling Grouped Actions and Sequential Edges

- If the information extraction output includes the `group` field, remember to:
    - Set `strict_group=True` when initializing `DisassemblyGraph`
    - **Uncomment** the following lines in `main.py` to enable step-by-step logic:
        
        ```python
        handler.create_task_nodes() # Build Task nodes for grouped actions
        handler.create_sequence_edges() # Create :NEXT relationships between ordered steps
        
        ```
        
- If the data **does not include** the `group` field:
    - Set `strict_group=False` (default)
    - Keep the above lines **commented out**, so the graph builder will skip sequential modeling.
