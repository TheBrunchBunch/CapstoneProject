## Structured Extraction of Mechanical Disassembly Knowledge

This project focuses on extracting structured disassembly knowledge from mechanical literature and web content. The core goal is to identify the tools (Tool), actions (Action), and components (Component) involved in disassembly processes and represent them as structured triplets, forming a machine-readable engineering knowledge graph for downstream applications such as remanufacturing and maintenance. The pipeline integrates Semantic Role Labeling (SRL) and inference from local Large Language Models (LLMs) to ensure semantic accuracy, structural integrity, and traceability of information.

## Environment Requirements

### AllenNLP Module

The `nlp.py` module relies on AllenNLP for semantic role labeling. On macOS, AllenNLP may cause dependency conflicts with other libraries such as `transformers` and `torch`. Therefore, it is strongly recommended to run this module separately using the official AllenNLP Docker image.

- Recommended image: `allennlp/allennlp:v2.10.1`
- You may build using `Dockerfile.allennlp` if customization is needed

### General Runtime for Other Modules

Other modules such as data cleaning, LLM validation, and final output generation are designed for local execution. It is recommended to use Python 3.9 or later.

Required Python packages include:
- `spacy >= 3.7.2`
- `torch >= 2.0.0`
- `transformers >= 4.30.0`
- `fitz` (PyMuPDF)
- `tqdm`
- `requests`
- `nltk`
- `gdown`
- `numpy`
- `pydantic`

Before running, make sure to download the required models and data:
- For spaCy: `python -m spacy download en_core_web_sm`
- For NLTK: `nltk.download('punkt')`

This project requires a local instance of Ollama running on port 11434 to host the LLaMA 3.2 model for semantic validation and triplet generation.

## Project Directory Structure and Workflow

The project structure is organized as follows:
- `documents/`: Stores raw PDF documents for disassembly literature
- `download.py`: Script to download PDF documents from Google Drive
- `dataclean.py`: Script to clean and extract paragraphs from PDFs
- `dataclean_search.py`: Script to clean web content from scraped search results
- `nlp.py`: Performs SRL-based extraction of subject–predicate–object triplets using AllenNLP
- `llm.py`: Uses local LLaMA models to verify and structure disassembly triplets
- `requirements.txt`: Lists all Python dependencies for local modules

### Input and Output Files

**Input Files**
- `paper_database.papers.json`: Metadata for each input document, including title, file name, and source URL
- `paper_database.search_results.json`: Raw web search results collected via Google Custom Search

**Intermediate Outputs**
- `cleaned_data.json`: Cleaned paragraphs extracted from PDF files
- `cleaned_search_results.json`: Cleaned text content from web search results
- `srl_triplets_combined.json`: Triplets extracted using semantic role labeling

**Final Outputs**
- `disassembly_structured_output.json`: Final tool–action–component triplets with source URL after LLM validation
- `converted_disassembly_data.json`: Triplets converted into a format compatible with downstream database ingestion

### Pipeline Overview

1. Place PDF documents in the `documents/` directory or use `download.py` to fetch them automatically.
2. Clean the textual data by running `dataclean.py` for PDFs and `dataclean_search.py` for web content.
3. Run `nlp.py` using the AllenNLP container to extract semantic triplets.
4. Execute `llm.py` to verify and structure the triplets using a local LLaMA model through the Ollama framework.

### Notes

To avoid library conflicts, particularly on macOS, please isolate the SRL pipeline (`nlp.py`) in an AllenNLP environment. All other components are compatible with standard Python environments. Ensure that Ollama is correctly installed and the local LLM server is active before running the `llm.py` module.

This setup ensures a fully traceable, high-precision knowledge extraction workflow for disassembly-related engineering tasks.

