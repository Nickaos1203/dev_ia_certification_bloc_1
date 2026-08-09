from pathlib import Path

import scrapy


class VideogamesSpider(scrapy.Spider):
    name= "videogames_spider"


    async def start(self):
        pages_urls = ["https://www.metacritic.com/browse/game/?releaseYearMin=2025&releaseYearMax=2026&page=" + str(x) for x in range(1, 5)]
        for url in pages_urls:
            yield scrapy.Request(
                url=url, 
                callback=self.parse)


    def parse(self, response):
        urls = response.css('div[data-testid="filter-results"] a::attr(href)').getall()
        
        for url in urls:
            yield response.follow(
                url,
                callback=self.parse_videogames
            )


    def parse_videogames(self, response):
        yield {
            "url" : response.url
        }


        # url = ""
        # nom = ""
        # date = ""
        # plateformes = ""
        # editeur = ""
        # genre = ""
        # resume = ""
        # note_metascore = ""
        # note_utilisateur = ""
        # pourcentage_note_positif = ""
        # pourcentage_note_negatif = ""
        # pourcentage_note_mixte = ""
