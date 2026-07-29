import scrapy


class EventItem(scrapy.Item):
    titre = scrapy.Field()
    date = scrapy.Field()
    lieu = scrapy.Field()
    url = scrapy.Field()