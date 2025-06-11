import requests
from pymongo import MongoClient

# your Google API key and custom search engine ID
API_KEY = "AIzaSyCprzBHuE3zPxyPtbS73OwYs_fqXGjCZto"        # replace with your API key
SEARCH_ENGINE_ID = "31e2bc994edf1435e"  # replace with your search engine ID

def main():
    keyword = input("Please Input Keyword: ").strip()
    if not keyword:
        print("Keyword cannot be empty.")
        return

    # construct Google Custom Search API URL
    # default to return the first 10 results (start parameter defaults to 1, returning 10 results)
    api_url = (f"https://www.googleapis.com/customsearch/v1?key={API_KEY}"
               f"&cx={SEARCH_ENGINE_ID}&q={requests.utils.requote_uri(keyword)}")

    # Setting HTTP request headers and timeout
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/102.0.0.0 Safari/537.36"
    }
    timeout = 10  # seconds

    try:
        response = requests.get(api_url, headers=headers, timeout=timeout)
        response.raise_for_status()  # if the response was unsuccessful, raise an HTTPError
    except requests.RequestException as e:
        print(f"Error: {e}")
        return

    data = response.json()
    items = data.get("items")
    if not items:
        print("No results found for the keyword.")
        return

    # connect to MongoDB and insert the search results
    client = MongoClient("mongodb://localhost:27017/")
    db = client["paper_database"]
    collection = db["search_results"]

    inserted_count = 0
    for index, item in enumerate(items):
        url = item.get("link")  # get the URL from the search result
        if not url:
            continue  # skip if no URL is found
        doc = {"keyword": keyword, "index": index, "url": url}
        try:
            # search for existing document to avoid duplicates
            if collection.find_one({"keyword": keyword, "url": url}) is None:
                collection.insert_one(doc)
                inserted_count += 1
        except Exception as db_error:
            print(f"DataBase Error: {db_error}")
    client.close()
    print(f"Keyword '{keyword}' searching completed, inserted {inserted_count} new records into MongoDB.")

if __name__ == "__main__":
    main()
