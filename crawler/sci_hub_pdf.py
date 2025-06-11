import requests
from bs4 import BeautifulSoup
import time  # import time module

# test paper URL
# paper_url = "https://ieeexplore.ieee.org/abstract/document/9269520/"


def get_pdf(paper_url):
    # request headers
    scihub_url = f"https://sci-hub.se/{paper_url}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        # visit the Sci-Hub page
        response = requests.get(scihub_url, headers=headers, timeout=10)
        
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

        pdf_response = requests.get(pdf_url, headers=headers, timeout=10)

        if pdf_response.status_code == 200:
            print(f"PDF Downloaded.")
            return pdf_response.content
        else:
            print(f"Failed to download PDF. Status code: {pdf_response.status_code}")
            return None
        
    except Exception as e:
        print(f"Error fetching PDF: {e}")
        return None