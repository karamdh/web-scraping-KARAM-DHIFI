import scrapy

from niceagenda.items import EventItem


class EventsSpider(scrapy.Spider):
    name = "events"
    start_urls = ["https://www.jds.fr/nice/agenda/"]

    custom_settings = {
        "DOWNLOAD_DELAY": 1.0,
        "ROBOTSTXT_OBEY": True,
    }

    def parse(self, response):
        titres = response.css("a.font-size-20")
        dates = response.css("span.font-size-14::text").getall()
        lieux = response.css("a[href*='_L']::text").getall()

        for i, lien in enumerate(titres):
            yield EventItem(
                titre=lien.css("::text").get("").strip(),
                url=lien.attrib.get("href", ""),
                date=dates[i].strip() if i < len(dates) else "",
                lieu=lieux[i].strip() if i < len(lieux) else "",
            )