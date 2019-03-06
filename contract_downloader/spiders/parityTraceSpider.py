import scrapy
import pickle
from pyquery import PyQuery as pq
import json
# from action import ParityTrace

class ContractSpider(scrapy.spiders.Spider):

    name = "parityspider"
    tx_url = r'https://etherscan.io/vmtrace?txhash='
    param = r'&type=parity#raw'
    logfile = 'log.txt'
    errorfile = 'errorlog.txt'

    pageinfo = {}

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
    }

    def start_requests(self):
        # get txhash
        tx_hash_list = ['0xdb4ce0f0cc8a4a273e61c10aefc8ea5949e1ce768da9de4d808dc21bbba03a39']
        for tx_hash in tx_hash_list:
            yield scrapy.Request(self.tx_url + tx_hash + self.param, headers=self.headers)

    def parse(self, response):
        dom = pq(response.body)
        raw_parity_json = dom("div#ContentPlaceHolder1_raw")("div.card-body")("pre").html()
        parity_trace_json = json.loads('['+raw_parity_json+']')
        parity_traces = []
        for action in parity_trace_json:
            parity_traces.append((action['action']['from'],
                                 action['action']['to'],
                                 action['action']['input'][2:10] if len(action['action']['input']) >= 10 else '',
                                action['traceAddress']))
        contrace_path = 'paritytrace'
        f = open(contrace_path, 'wb')
        pickle.dump(parity_traces, f)
