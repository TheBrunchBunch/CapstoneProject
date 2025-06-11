import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup

def extract_text_from_url(url, min_length=50):
    """
    Scrapes the webpage content and extracts all paragraphs longer than min_length,
    """
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Request Fail {url}: {e}")
        return None

    if "text/html" not in response.headers.get("Content-Type", ""):
        print(f"Skip non-HTML page: {url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    contents = [
        p.get_text(strip=True) for p in paragraphs
        if len(p.get_text(strip=True)) > min_length
    ]

    return " ".join(contents) if contents else None


def main():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["paper_database"]
    collection = db["search_results"]

    records = collection.find()
    updated_count = 0

    for record in records:
        keyword = record.get("keyword")
        index = record.get("index")
        url = record.get("url")

        if not url:
            continue

        print(f"Processing: [{keyword}] #{index} - {url}")

        if 'content' in record:
            print("Duplicated record, skipping...")
            continue

        full_text = extract_text_from_url(url)
        if full_text:
            result = collection.update_one(
                {"keyword": keyword, "index": index, "url": url},
                {"$set": {"content": full_text}}
            )
            if result.modified_count:
                print("Updated content successfully.")
                updated_count += 1
        else:
            print("No content extracted or already exists.")

    client.close()
    print(f"Finished, {updated_count} records updated with content.")


if __name__ == "__main__":
    main()

