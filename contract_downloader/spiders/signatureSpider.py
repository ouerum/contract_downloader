import scrapy
import pickle
from pyquery import PyQuery as pq
import re
import json
from contract_downloader.items import SigHex

class ContractSpider(scrapy.spiders.Spider):

    name = "signatureSpider"
    tx_url = r'https://www.4byte.directory/api/v1/signatures/?format=json&page='
    page_num = 1440

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
    }

    def start_requests(self):
        for num in range(self.page_num):
            yield scrapy.Request(self.tx_url + str(num+1), headers=self.headers)

    def parse(self, response):
        data = json.loads(response.body)
        results = data['results']
        for result in results:
            item = SigHex()
            item['sig'] = result['hex_signature']
            item['hex'] = result['text_signature']
            yield item


