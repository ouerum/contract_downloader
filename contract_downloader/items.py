# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ContractDownloaderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    pass


class SigHex(scrapy.Item):
    hex = scrapy.Field()
    sig = scrapy.Field()
    pass