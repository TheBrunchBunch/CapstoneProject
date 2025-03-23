import web_crawler
import sci_hub_pdf
import json
import requests
import csv
import os

# Drive API 3 token, for uploading files to Google Drive
token = "ya29.a0AeXRPp6nHl4d3KvN-519DkouX_qFJITP3rXyban7oB8HvOchQA7wBv6UEq7aD0lUFR0CLIPj0PQqpuiwNSvpCY9bmPUhaAJK6BEduv74W_PfBwhCxQTVpf38zHfJPr7LuJsx6rlV12nLrp8TOdR6XNaDlHfLptqbmbVUxYgHaCgYKAWkSAQ4SFQHGX2MiG6kqDaBSfEYJmshpOSeF2w0175"
# instance of the folder where the files will be uploaded
folder_id = "1v2yiyaHoPmF4rzGl7ZTKmXcOMXjJxZ7p"


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
                pdf_bytes = sci_hub_pdf.get_pdf(url)
                if pdf_bytes:
                    upload_name = f"query_{query}_paper_{i}.pdf"
                    upload_to_drive(upload_name, folder_id, token, pdf_bytes)


main()
# paper_url = "https://ieeexplore.ieee.org/abstract/document/9269520/"
# upload_to_drive("test.pdf", folder_id, token, sci_hub_pdf.get_pdf(paper_url))
