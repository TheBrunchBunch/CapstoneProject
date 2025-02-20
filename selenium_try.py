from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# 配置无头模式（可选）
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式，不打开浏览器窗口
chrome_options.add_argument("--disable-gpu")

# 自动下载并使用正确的 `chromedriver`
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 访问网页
url = "https://www.sciencedirect.com/science/article/pii/S2212827116002237"
driver.get(url)

page_text = driver.find_element(By.TAG_NAME, "section").text
print(page_text)

# 关闭浏览器
driver.quit()

