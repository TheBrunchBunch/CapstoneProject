import requests
from bs4 import BeautifulSoup
import time  # import time module

# paper URL
paper_url = "https://ieeexplore.ieee.org/abstract/document/9269520/"

save_path = "../documents/"

def get_pdf(paper_url, save_path, save_name):
    # request headers
    scihub_url = f"https://sci-hub.se/{paper_url}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    # visit the Sci-Hub page
    response = requests.get(scihub_url, headers=headers)
    
    # wait for 3 seconds to allow the page to load
    time.sleep(3)
    
    soup = BeautifulSoup(response.text, "html.parser")

    # look for the PDF URL
    pdf_url = None
    for embed in soup.find_all("embed"):
        src = embed.get("src")
        if "pdf" in src:
            pdf_url = src
            break

    # download the PDF
    if pdf_url is None:
        print("PDF Unavailable")
        return 0
    if pdf_url[0:2] == "//":
        pdf_url = "https:" + pdf_url
    elif pdf_url[0] == "/":
        pdf_url = "https://sci-hub.se" + pdf_url  # prepend the domain
    else:
        return 0

    print("PDF link:", pdf_url)

    # wait for 3 seconds before downloading the PDF
    time.sleep(3)

    pdf_response = requests.get(pdf_url, headers=headers)

    file_name = save_path + save_name
    with open(file_name, "wb") as f:
        f.write(pdf_response.content)
        
    print(f"Downloaded: {file_name}")
    return 1