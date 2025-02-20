import requests
from bs4 import BeautifulSoup

# paper URL
paper_url = "https://link.springer.com/chapter/10.1007/978-3-030-05931-6_6"
scihub_url = f"https://sci-hub.se/{paper_url}"
save_path = "documents/"


def get_pdf(scihub_url, save_path):
    # request headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    # visit the Sci-Hub page
    response = requests.get(scihub_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # look for the PDF URL
    pdf_url = None
    for embed in soup.find_all("embed"):
        src = embed.get("src")
        if "pdf" in src:
            pdf_url = src
            break

    # download the PDF
    if pdf_url:
        pdf_url = "https://sci-hub.se" + pdf_url  # prepend the domain

        print("PDF link:", pdf_url)

        pdf_response = requests.get(pdf_url, headers=headers)
        
        file_name = save_path + "paper.pdf"
        with open(file_name, "wb") as f:
            f.write(pdf_response.content)
        
        print(f"Downloaded: {file_name}")
    else:
        print("PDF Unavailable")


get_pdf(scihub_url, save_path)