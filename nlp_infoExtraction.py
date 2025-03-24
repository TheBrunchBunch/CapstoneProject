#pdf pre-processing
import fitz  
import re

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text_pages = []
    
    for page in doc:
        text = page.get_text()
        text = clean_text(text)
        if text.strip():
            text_pages.append(text)
    
    return text_pages

def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = text.strip()
    return text

def split_into_paragraphs(text_pages):
    paragraphs = []
    for page in text_pages:
        paras = re.split(r'\n{2,}', page) 
        paras = [p.strip() for p in paras if p.strip()]
        paragraphs.extend(paras)
    return paragraphs

pdf_path = 'query_discrete components disassembly_paper_1.pdf'  
raw_text = extract_text_from_pdf(pdf_path)
paragraphs = split_into_paragraphs(raw_text)

"""
#test pdf pre-processing
for i, para in enumerate(paragraphs[:5]):
    print(f"[para{i+1}] {para}\n")
"""

#auto-generate json patterns for ner
import pandas as pd
import json

file_path = "副本20241210_Disassembly database.xlsx"
df = pd.read_excel(file_path)

label_map = {
    "Type of component": "COMPONENT_TYPE",
    "State of component": "STATE",
    "Component": "COMPONENT",
    "Method": "METHOD",
    "Tool": "TOOL",
    "Time (Seconds)": "DURATION"
}

def generate_spacy_patterns(df, label_map):
    patterns = []
    for column, label in label_map.items():
        if column in df.columns:
            values = df[column].dropna().unique()
            for val in values:
                val_str = str(val).strip()
                if not val_str:
                    continue

                #  METHOD： LEMMA match
                if label == "METHOD":
                    patterns.append({
                        "label": label,
                        "pattern": [{"LEMMA": val_str.lower()}]
                    })
                #  TOOL：Regular Expressions
                elif label == "TOOL" and not val_str.endswith("s"):
                    patterns.append({
                        "label": label,
                        "pattern": val_str
                    })
                    patterns.append({
                        "label": label,
                        "pattern": val_str + "s"
                    })
                else:
                    # default
                    patterns.append({
                        "label": label,
                        "pattern": val_str
                    })
    return patterns

patterns = generate_spacy_patterns(df, label_map)
output_path = "custom_entity_patterns.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(patterns, f, indent=2, ensure_ascii=False)

print(f"Successfully generated {len(patterns)} entity recognition rules, saved as: {output_path}")



#NER
import spacy
from spacy.pipeline import EntityRuler
from spacy.lang.en import English
import json
nlp = English()

nlp.add_pipe("lemmatizer", config={"mode": "rule"})
nlp.initialize()
ruler = nlp.add_pipe("entity_ruler")
with open("custom_entity_patterns.json", "r", encoding="utf-8") as f:
    custom_patterns = json.load(f)
ruler.add_patterns(custom_patterns)

def extract_entities(paragraphs, nlp_model):
    all_results = []
    for i, para in enumerate(paragraphs):
        doc = nlp_model(para)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        all_results.append({
            "paragraph_index": i,
            "text": para,
            "entities": entities
        })
    return all_results

results = extract_entities(paragraphs, nlp)

for r in results[:5]:
    print(f"\n[paragraph: {r['paragraph_index']}]")
    print("🔍 entities：", r["entities"])

#re
def extract_relations(text, entities):
    
    tools = [ent for ent, label in entities if label == "TOOL"]
    methods = [ent for ent, label in entities if label == "METHOD"]
    components = [ent for ent, label in entities if label == "COMPONENT"]

    relations = []

    # TOOL - PERFORMS -> METHOD
    for tool in tools:
        for method in methods:
            if abs(text.find(tool) - text.find(method)) < 50:
                relations.append((tool, "PERFORMS", method))

    # METHOD - ACTS_ON -> COMPONENT
    for method in methods:
        for comp in components:
            if abs(text.find(method) - text.find(comp)) < 50:
                relations.append((method, "ACTS_ON", comp))

    return relations

re_results = []

for r in results:
    para_idx = r["paragraph_index"]
    text = r["text"]
    entities = r["entities"]

    relations = extract_relations(text, entities)
    for h, rel, t in relations:
        re_results.append({
            "paragraph_index": para_idx,
            "text": text,
            "head": h,
            "relation": rel,
            "tail": t
        })

#store results for database input
import pandas as pd

re_df = pd.DataFrame(re_results)
re_df.to_csv("relations.csv", index=False)


entity_set = set()

def get_label(entity_text, entity_list):
    for ent_text, ent_label in entity_list:
        if ent_text == entity_text:
            return ent_label
    return "UNKNOWN"

for r in re_results:
    entity_set.add((r["head"], get_label(r["head"], r["text"])))
    entity_set.add((r["tail"], get_label(r["tail"], r["text"])))

nodes_df = pd.DataFrame(list(entity_set), columns=["id", "label"])
nodes_df.to_csv("nodes.csv", index=False)

