import scrapy

class MySpider(scrapy.Spider):
    name = "my_spider"
    start_urls = ["https://www.sciencedirect.com/science/article/pii/S2212827116002237"]

    def parse(self, response):
        # 提取网页中的文本
        text = response.xpath("//body//text()").getall()
        yield {"text": " ".join(text)}
