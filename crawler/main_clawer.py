import web_crawler
import sci_hub_pdf
import json
import requests
import csv
import os
from pymongo import MongoClient


# Drive API 3 token, for uploading files to Google Drive from this link: https://developers.google.com/oauthplayground
token = "your own key"
# instance of the folder where the files will be uploaded
folder_id = "your folder id"


def insert_into_mongodb(keyword, index, url):
    client = MongoClient("mongodb://localhost:27017/")  # local MongoDB server
    db = client["paper_database"]                      # database name
    collection = db["papers"]                          # collection name
    doc = {
        "keyword": keyword,
        "index": index,
        "url": url
    }
    if not collection.find_one({"keyword": keyword, "url": url}):
        collection.insert_one(doc)
    client.close()



def upload_to_drive(upload_name, folder_id, token, file_bytes):
    headers = {"Authorization": "Bearer " + token}
    para = {
        "name": upload_name,
        "parents": [folder_id]
    }

    files = {
        'data': ('metadata', json.dumps(para), 'application/json; charset=UTF-8'),
        'file': (upload_name, file_bytes, 'application/pdf')
    }

    r = requests.post(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
        headers=headers,
        files=files
    )
    print(r.text)


def main():
    query = input("Enter the query: ")
    confirm = input(f"Are you sure you want to download papers for the query '{query}'? (y/n): ")
    if confirm.lower() != "y":
        print("Exiting...")
        return
    save_path = "../links/"
    # if the csv file already exists, then use the existing file
    if not os.path.exists(f"{save_path}article_{"industry disassembly "+query}.csv"):
        web_crawler.get_info_from_qurey("industry disassembly "+query, save_path)
    else:
        print(f"File {save_path}article_{"industry disassembly "+query}.csv already exists")

    # get url from the csv file
    with open(f"{save_path}article_{"industry disassembly "+query}.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row, i in zip(reader, range(10)):
            url = row['URL']
            if url != "NA":
                insert_into_mongodb(query, i, url)
                pdf_bytes = sci_hub_pdf.get_pdf(url)
                if pdf_bytes:
                    upload_name = f"query_{"industry disassembly "+query}_paper_{i}.pdf"
                    upload_to_drive(upload_name, folder_id, token, pdf_bytes)


main()
