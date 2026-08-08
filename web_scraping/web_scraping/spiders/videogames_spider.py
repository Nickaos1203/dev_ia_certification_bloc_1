from pathlib import Path

import scrapy


class VideogamesSpider(scrapy.Spider):
    name= "dishe_spider"
    allowed_domains = ["metacritic.com"]
    start_urls = ["https://www.metacritic.com/browse/game/?releaseYearMin=2025&releaseYearMax=2026&page=" + str(x) for x in range(1, 10)]

    async def start(self):
        urls = [
            "https://quotes.toscrape.com/page/1/",
            "https://quotes.toscrape.com/page/2/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")