import json
import re
import spacy
from tqdm import tqdm

#spaCy English sentence segmentation model
nlp = spacy.load("en_core_web_sm")

SEARCH_RESULTS_JSON_PATH = "/Users/dshim/Desktop/capstone_final/paper_database.search_results.json"
OUTPUT_JSON_PATH = "cleaned_search_results.json"
MAX_PARAGRAPH_LEN = 800

#Load search_results.json
with open(SEARCH_RESULTS_JSON_PATH, "r", encoding="utf-8") as f:
    search_results = json.load(f)

def clean_text(text):
    if not text:
        return ""
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

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
        if len(buffer) + len(s) + 1 <= max_len:
            buffer += " " + s if buffer else s
        else:
            if buffer.strip():
                paragraphs.append({"text": buffer.strip(), "url": url})
            buffer = s
    if buffer.strip():
        paragraphs.append({"text": buffer.strip(), "url": url})
    return paragraphs

all_paragraphs = []
for entry in tqdm(search_results, desc="Processing search_results"):
    url = entry.get("url", "")
    content = clean_text(entry.get("content", ""))
    if not content:
        continue
    paras = split_paragraphs(content, url, MAX_PARAGRAPH_LEN)
    all_paragraphs.extend(paras)

with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(all_paragraphs, f, ensure_ascii=False, indent=2)

print(f"\nSuccessfully extracted {len(all_paragraphs)} paragraphs, saved to {OUTPUT_JSON_PATH}")