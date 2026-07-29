import scrapy

from boursorama.items import ActionItem


class CacSpider(scrapy.Spider):
    name = "cac"
    start_urls = ["https://www.boursorama.com/bourse/actions/palmares/france/"]

    custom_settings = {
        "DOWNLOAD_DELAY": 1.0,
        "ROBOTSTXT_OBEY": True,
    }

    def parse(self, response):
        rows = response.css("table.c-table tbody tr")
        for row in rows:
            lien = row.css("a")
            href = lien.attrib.get("href", "")
            # Extraire le code ISIN depuis l'URL (ex: /cours/1rPATE/ -> 1rPATE)
            isin = href.strip("/").split("/")[-1] if href else ""

            libelle = lien.css("::text").get("").strip()

            cours_raw = row.css("span.c-instrument--last::text").get("0")
            variation_raw = row.css("span.c-instrument--instant-variation::text").get("0")
            volume_raw = row.css("span.c-instrument--totalvolume::text").get("0")

            try:
                cours = float(cours_raw.replace(",", ".").strip())
            except (ValueError, AttributeError):
                cours = 0.0

            try:
                variation = float(
                    variation_raw.replace(",", ".").replace("%", "").replace("+", "").strip()
                )
            except (ValueError, AttributeError):
                variation = 0.0

            try:
                volume = int(volume_raw.replace(" ", "").replace("\xa0", "").strip() or 0)
            except (ValueError, AttributeError):
                volume = 0

            yield ActionItem(
                libelle=libelle,
                cours=cours,
                variation=variation,
                volume=volume,
                isin=isin,
            )