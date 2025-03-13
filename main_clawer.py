import web_crawler
import sci_hub_pdf
import json
import requests
import csv
import os

token = "ya29.a0AeXRPp41IwFaGVkIL6zLw-WtMjY_5cpYx96NLjojoVA-g-XAfBL6wEVteW2LRjI3LGN2HvXj3RYAlWDdJ68lyCKgr4rVycTgXUVN7SWXDRek6B25BBsq2hF1GVT7suTVuf2Zxw1jScl0avhmOL7t9-UyQUuaoUgwnJEgBEkiaCgYKATISAQ4SFQHGX2MiGqO0h1lVjKp9NEV8r90-fA0175"
folder_id = "1v2yiyaHoPmF4rzGl7ZTKmXcOMXjJxZ7p"
file_name = "../documents/paper.pdf"
upload_name = "paper.pdf"
def upload_to_drive(upload_name, folder_id, token, file_name):
    headers = {"Authorization": "Bearer " + token}
    para = {
        "name": upload_name,
        "parents": [folder_id]
    }

    files = {
        'data': ('metadata', json.dumps(para), 'application/json; charset=UTF-8'),
        'file': open(file_name, "rb")
    }

    r = requests.post(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
        headers=headers,
        files=files
    )
    print(r.text)


def main():
    query = "discrete components disassembly"
    save_path = "../links/"
    # if the csv file already exists, then use the existing file
    if not os.path.exists(f"{save_path}article_{query}.csv"):
        web_crawler.get_info_from_qurey(query, save_path)
    else:
        print(f"File {save_path}article_{query}.csv already exists")

    # get url from the csv file
    with open(f"{save_path}article_{query}.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row, i in zip(reader, range(100)):
            url = row['URL']
            if url != "NA":
                if sci_hub_pdf.get_pdf(url, "../documents/", f"query_{query}_paper_{i}.pdf") == 1:
                    upload_name = f"query_{query}_paper_{i}.pdf"
                    file_name = f"../documents/query_{query}_paper_{i}.pdf"
                    upload_to_drive(upload_name, folder_id, token, file_name)


main()