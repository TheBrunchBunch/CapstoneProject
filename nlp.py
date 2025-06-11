import os
import json
import re
from tqdm import tqdm
from nltk.tokenize import sent_tokenize
from allennlp.predictors.predictor import Predictor
import allennlp_models.structured_prediction

# SRL model 
SRL_MODEL_PATH = "https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.11.19.tar.gz"
print("Loading SRL model...")
predictor = Predictor.from_path(SRL_MODEL_PATH)

#Input
SEARCH_RESULTS_PATH = "/capstone_final/cleaned_search_results.json"
CLEANED_DATA_PATH = "/capstone_final/cleaned_data.json"
OUTPUT_PATH = "/capstone_final/srl_triplets_combined.json"


def extract_triplets(text):
    triplets = []
    try:
        sentences = sent_tokenize(text)
        for sent in sentences:
            if len(sent.strip()) < 20:
                continue
            result = predictor.predict(sentence=sent)
            for verb in result.get("verbs", []):
                desc = verb["description"]
                subj = re.search(r"\[ARG0: (.*?)\]", desc)
                pred = re.search(r"\[V: (.*?)\]", desc)
                obj = re.search(r"\[ARG1: (.*?)\]", desc)
                if subj and pred and obj:
                    triplets.append({
                        "subject": subj.group(1),
                        "predicate": pred.group(1),
                        "object": obj.group(1)
                    })
    except Exception as e:
        print(f"Failed to process sentence: {e}")
    return triplets

#Load and process
def load_and_extract(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    extracted = []
    for i, item in enumerate(tqdm(data, desc=f"Processing {os.path.basename(path)}")):
        text = item.get("text", "")
        url = item.get("url", "")
        if not text.strip():
            continue
        triplets = extract_triplets(text)
        extracted.append({
            "paragraph_id": i + 1,
            "text": text,
            "url": url,
            "triplets": triplets
        })
    return extracted

#Merge two datasets and output
def main():
    results = load_and_extract(SEARCH_RESULTS_PATH) + load_and_extract(CLEANED_DATA_PATH)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nDone! Extracted from {len(results)} paragraphs. Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()