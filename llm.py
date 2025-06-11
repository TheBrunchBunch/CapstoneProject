import json
import re
import requests
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

#Phase 1-relevance
def is_relevant_triplet(subject, predicate, obj):
    prompt = f"""
You are a mechanical disassembly classifier.

You are given a semantic triplet extracted from a sentence:

Tool: {subject}
Action: {predicate}
Object: {obj}

Determine whether this triplet describes a physical disassembly action involving:
- a real-world tool or agent (e.g. wrench, hammer),
- a physical object/component (e.g. bolt, panel),
- a mechanical action (e.g. remove, unscrew, break).

Only answer "yes" or "no".
""".strip()

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2:latest", "prompt": prompt, "stream": False}
        )
        answer = response.json().get("response", "").strip().lower()
        return "yes" in answer
    except Exception as e:
        print("Phase 1 failed:", e)
        return False

#Phase 2-triplets
def extract_disassembly_steps(paragraph):
    prompt = f"""
You are a disassembly process analyzer.

Based on the paragraph below, extract all physical disassembly steps.

Constraints:
- Each step must follow this format: [TOOL] – [ACTION] – [COMPONENT]
- All three elements must appear exactly in the paragraph text.
- Do NOT invent tools, actions, or components.
- Only include steps describing actual mechanical disassembly actions.
- If multiple steps are found, number them.

Output Format:
1. [TOOL] – [ACTION] – [COMPONENT]
2. ...

Paragraph:
{paragraph}

Only return disassembly steps. No explanation or markdown.
""".strip()

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2:latest", "prompt": prompt, "stream": False}
        )
        return response.json().get("response", "").strip()
    except Exception as e:
        print("Phase 2 failed:", e)
        return ""

def parse_steps_to_triplets(llm_output):
    steps = []
    for line in llm_output.splitlines():
        match = re.match(r"(\d+)[\.\s]+(.+?)\s*[-–]\s*(.+?)\s*[-–]\s*(.+)", line)
        if match:
            steps.append({
                "order": int(match.group(1)),
                "tool": match.group(2).strip(),
                "method": match.group(3).strip(),
                "object": match.group(4).strip()
            })
    return steps
#grounding
def fuzzy_in(paragraph, keyword, threshold=0.8):
    paragraph = paragraph.lower()
    keyword = keyword.lower()
    words = paragraph.split()
    return any(SequenceMatcher(None, word, keyword).ratio() > threshold for word in words)

def clean_triplets_in_text(paragraph, triplets):
    cleaned = []
    for t in triplets:
        match_score = sum(
            fuzzy_in(paragraph, t.get(key, "")) for key in ["tool", "method", "object"]
        )
        if match_score >= 2:
            cleaned.append(t)
    return cleaned

#url match
def process_paragraph(item):
    para_id = item.get("paragraph_id")
    paragraph = item.get("text", "")
    srl_triplets = item.get("triplets", [])
    url = item.get("url", "")

    #Phase 1
    relevant = []
    for t in srl_triplets:
        try:
            subj = t["subject"]
            pred = t["predicate"]
            obj = t["object"]
            if is_relevant_triplet(subj, pred, obj):
                relevant.append({
                    "tool": subj,
                    "method": pred,
                    "object": obj
                })
        except KeyError:
            continue

    if not relevant:
        return []

    #Phase 2:
    raw_output = extract_disassembly_steps(paragraph)
    structured = parse_steps_to_triplets(raw_output)
    filtered = clean_triplets_in_text(paragraph, structured)
    return [{
        "tool": t["tool"],
        "action": t["method"],
        "component": t["object"],
        "source": url
    } for t in filtered]

def process_file(input_path, output_path, max_workers=4):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    flat_results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_paragraph, item): item for item in data}
        for future in tqdm(as_completed(futures), total=len(data), desc="Processing paragraphs"):
            try:
                flat_results.extend(future.result())
            except Exception as e:
                print(f"Skipped paragraph due to error: {e}")

    #Save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(flat_results, f, indent=2, ensure_ascii=False)

    print(f"\nExtraction complete. {len(flat_results)} triplets saved to: {output_path}")

if __name__ == "__main__":
    process_file(
        input_path="/Users/dshim/Desktop/capstone_final/srl_triplets_combined.json",
        output_path="/Users/dshim/Desktop/capstone_final/disassembly_structured_output.json",
        max_workers=4 
    )