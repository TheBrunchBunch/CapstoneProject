import os
import re
import json
import fitz 
import spacy
from tqdm import tqdm
#Initialize
nlp = spacy.load("en_core_web_sm")
PDF_DIR = "./documents"
PAPERS_JSON_PATH = "paper_database.papers.json"
SEARCH_RESULTS_JSON_PATH = "/Users/dshim/Desktop/capstone_final/paper_database.search_results.json"
OUTPUT_JSON_PATH = "cleaned_data.json"
MAX_PARAGRAPH_LEN = 800
# Load Metadata
def load_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load file {file_path}: {e}")
        return []
#two data sources
papers_data = load_json_file(PAPERS_JSON_PATH)
search_results = load_json_file(SEARCH_RESULTS_JSON_PATH)
# mapping: (keyword, index) -> {url, content}
def build_data_map(data_list):
    data_map = {}
    for entry in data_list:
        key = (entry["keyword"].strip(), entry["index"])
        data_map[key] = {
            "url": entry["url"],
            "content": entry.get("content", ""),  
            "source": "search_results" if "content" in entry else "papers"
        }
    return data_map

#merge
combined_data = build_data_map(papers_data)
search_data = build_data_map(search_results)
for key, value in search_data.items():
    if key in combined_data:
        combined_data[key].update(value)
    else:
        combined_data[key] = value

# keyword and index from PDF
def extract_keyword_index(filename):
    match = re.search(r"([A-Za-z\s]+)_paper_(\d+)\.pdf", filename)
    if match:
        keyword = match.group(1).strip().split()[-1]  
        index = int(match.group(2))
        return keyword, index
    return None, None

def clean_text(text):
    if not text:
        return ""
        
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r"\$.*?\$", "", text)  
    text = re.sub(r"\(cid:\d+\)", "", text)  
    text = re.sub(r"\s{2,}", " ", text)  
    text = re.sub(r"[\u200b\u2022•●▪■►➤➢◆▶★]", "", text) 
    text = re.sub(r"(©|\bpreprint\b|\barxiv\b).{0,50}", "", text, flags=re.IGNORECASE)  
    text = re.sub(r"^.{0,5}journal.{0,30}$", "", text, flags=re.IGNORECASE)  
    text = re.sub(r"(Figure|Table|Image)\s?\d+.*", "", text, flags=re.IGNORECASE) 
    text = re.sub(r'[^\x00-\x7F\u4e00-\x9fff]+', '', text)  
    text = re.sub(r'[^\w\s.,;:!?()\-\'"]', '', text)  
    return text.strip()
def is_reference_section(text):
    return bool(re.search(r"\b(references|bibliography|acknowledgments)\b", text, re.IGNORECASE))
def extract_full_text(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            blocks = page.get_text("blocks")
            blocks = sorted(blocks, key=lambda b: (b[1], b[0]))  
            for block in blocks:
                block_text = block[4].strip()
                if not block_text or len(block_text) < 20:
                    continue
                if is_reference_section(block_text):
                    return text
                cleaned = clean_text(block_text)
                if cleaned:
                    text += cleaned + " "
    except Exception as e:
        print(f"Extraction failed: {pdf_path} → {e}")
    return text

def split_paragraphs(text, url, max_len=MAX_PARAGRAPH_LEN):
    if not text:
        return []
        
    doc = nlp(text)
    paragraphs = []
    buffer = ""
    
    for sent in doc.sents:
        s = sent.text.strip()
        if not s:
            continue
        #max length
        if len(s) > max_len:
            if buffer.strip():
                paragraphs.append({"text": buffer.strip(), "url": url})
                buffer = ""
            
            parts = re.split(r'[,;:.]', s)
            current_part = ""
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                    
                if len(current_part) + len(part) + 1 <= max_len:
                    current_part += " " + part if current_part else part
                else:
                    if current_part:
                        paragraphs.append({"text": current_part.strip(), "url": url})
                    current_part = part
            
            if current_part:
                paragraphs.append({"text": current_part.strip(), "url": url})
            continue
            
        if len(buffer) + len(s) + 1 <= max_len:
            buffer += " " + s if buffer else s
        else:
            if buffer.strip():
                paragraphs.append({"text": buffer.strip(), "url": url})
            buffer = s
    
    if buffer.strip():
        paragraphs.append({"text": buffer.strip(), "url": url})
    
    return paragraphs# === Main logic ===
all_paragraphs = []
for fname in tqdm(os.listdir(PDF_DIR), desc="Processing PDF files"):
    if not fname.endswith(".pdf"):
        continue
    keyword, index = extract_keyword_index(fname)
    if keyword is None:
        continue

    data = combined_data.get((keyword, index))
    if not data:
        print(f"No matching data: ({keyword}, {index})")
        continue

    pdf_path = os.path.join(PDF_DIR, fname)
    full_text = extract_full_text(pdf_path)
    
    if (not full_text or len(full_text) < 100) and data.get("content"):
        full_text = data["content"]
    
    if not full_text or len(full_text) < 100:
        print(f"Content too short or extraction failed: {fname}")
        continue

    paras = split_paragraphs(full_text, data["url"], MAX_PARAGRAPH_LEN)
    all_paragraphs.extend(paras)
for (keyword, index), data in tqdm(combined_data.items(), desc="Processing search results"):
    if data["source"] == "search_results" and data.get("content"):
        paras = split_paragraphs(data["content"], data["url"], MAX_PARAGRAPH_LEN)
        all_paragraphs.extend(paras)

#output save
with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(all_paragraphs, f, ensure_ascii=False, indent=2)

print(f"\nSuccessfully extracted {len(all_paragraphs)} paragraphs, saved to {OUTPUT_JSON_PATH}")