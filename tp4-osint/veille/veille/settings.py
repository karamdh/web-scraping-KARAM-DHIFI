BOT_NAME = "veille"

SPIDER_MODULES = ["veille.spiders"]
NEWSPIDER_MODULE = "veille.spiders"

ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
    "veille.pipelines.CleanPipeline": 100,
    "veille.pipelines.SQLitePipeline": 200,
}

FEEDS = {
    "mentions.csv": {"format": "csv", "encoding": "utf-8", "overwrite": True},
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
