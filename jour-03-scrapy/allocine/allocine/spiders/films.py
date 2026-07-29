import scrapy
from scrapy_playwright.page import PageMethod


class FilmsSpider(scrapy.Spider):
    name = "films"

    async def start(self):
        yield scrapy.Request(
            "https://www.allocine.fr/film/meilleurs/",
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_timeout", 8000),
                ],
            },
        )

    def parse(self, response):
        self.logger.info(f"STATUS: {response.status}")
        titres = response.css("h2.meta-title a::attr(href)").getall()
        self.logger.info(f"NB LIENS TROUVES: {len(titres)}")