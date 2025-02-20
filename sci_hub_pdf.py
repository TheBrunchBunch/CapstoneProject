import requests
from bs4 import BeautifulSoup

# Springer 论文 URL（Sci-Hub 格式）
paper_url = "https://link.springer.com/chapter/10.1007/978-3-030-05931-6_6"
scihub_url = f"https://sci-hub.se/{paper_url}"

# 伪装浏览器请求
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

# 访问 Sci-Hub 页面
response = requests.get(scihub_url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# 查找 PDF 网址
pdf_url = None
for embed in soup.find_all("embed"):
    src = embed.get("src")
    if "pdf" in src:
        pdf_url = src
        break

# 下载 PDF 文件
if pdf_url:
    pdf_url = "https://sci-hub.se" + pdf_url  # 修正不完整的 URL

    print("🔗 论文 PDF 网址:", pdf_url)

    pdf_response = requests.get(pdf_url, headers=headers)
    
    file_name = "paper.pdf"
    with open(file_name, "wb") as f:
        f.write(pdf_response.content)
    
    print(f"Downloaded: {file_name}")
else:
    print("PDF Unavailable")
