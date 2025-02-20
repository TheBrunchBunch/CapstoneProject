from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def get_article_text(article_url):
    # set Selenium options(headless)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") 
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    # ChromeDriver
    from webdriver_manager.chrome import ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    website_type = article_url.split(".")[1]
    if website_type == "sciencedirect":
        first_element = "section"
        class_name = "sec001"
        second_element = "div"
    elif website_type == "springer":
        first_element = "div"
        class_name = "c-article-section__content"
        second_element = "p"
    elif website_type == "annualreviews":
        first_element = "div"
        class_name = "article-level-0-front-and-body"
        second_element = "p"
    else:
        print("Website not supported.")
        return None

    # visit the article page
    driver.get(article_url)

    # wait for the article Section to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )
    except:
        print("Article section not found.")
        driver.quit()
        return None

    # get the page source
    page_source = driver.page_source

    # parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    # extract all p sections from the article section
    article_section = soup.find(first_element, class_=class_name)
    if article_section:
        paragraphs = article_section.find_all(second_element)
        full_text = "\n".join([p.get_text() for p in paragraphs])
        driver.quit()
        return full_text
    else:
        print("\nNo article section found.")
        driver.quit()
        return None


get_article_text("https://www.sciencedirect.com/science/article/pii/S2212827124007686")