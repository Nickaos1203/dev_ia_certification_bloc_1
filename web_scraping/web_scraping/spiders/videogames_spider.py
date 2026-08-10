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
        titre = response.css("h1.hero-title__text::text").get()
        date = response.css("div.hero-release-date__value::text").get()
        plateformes = response.css("li.c-product-details__section__list-item::text").getall()
        editeur = response.css("a.c-product-detail-link::text").get()
        genre = response.css("span.global-link-button__label::text").get()
        description = response.css("span.text-base.leading-\\[1\\.75rem\\].text-gray-900::text").get()
        scores = response.css('span[data-testid="global-score-value"]::text').getall()
        score_metacritic = scores[0]
        score_utilisateurs = scores[1]




        yield {
            "url": response.url,
            "titre": titre,
            "plateformes": plateformes,
            "editeur": editeur,
            "genre": genre,
            "description": description,
            "score_metacritic": score_metacritic,
            "score_utilisateurs": score_utilisateurs
        }
