import scrapy
import re
import datetime
from pyquery import PyQuery as pq

class ContractSpider(scrapy.spiders.Spider):

    name = "contractspider"
    code_url = r'https://etherscan.io/address/'
    logfile = 'log.txt'
    errorfile = 'errorlog.txt'
    pageinfo = {}

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
    }

    def start_requests(self):
        yield scrapy.Request('https://etherscan.io/contractsVerified', headers=self.headers)

    def parse(self, response):
        dom = pq(response.body)
        profile = dom(".container.profile")(".row").eq(1)  #
        regex = re.compile(r'A Total Of (\d+) verified contract source codes found')
        totalInfo = profile.children(".col-sm-6").eq(0).children("span").eq(0)
        m = regex.match(totalInfo.text())
        totalCount = 0
        if m:
            totalCount = m.group(1)
        lastHref = profile.children(".col-sm-6").eq(1)(".btn.btn-default.btn-xs.logout").eq(1).attr("href")
        lastregex = re.compile(r'/contractsVerified/(\d+)')
        m = lastregex.match(lastHref)
        pageSize = 0
        if m:
            pageSize = m.group(1)
        d = {"totalCount": totalCount, "pageSize": pageSize}
        for i in range(int(d["pageSize"])):
            yield scrapy.Request('https://etherscan.io/contractsVerified' +'/'+ str(i+1), headers=self.headers,callback=self.parse_Page)
        # yield scrapy.Request('https://etherscan.io/address/0xe7f648ad1f726a7f81cc7101a3c3b18a94a1c3a9#code', headers=self.headers, callback=self.getContract)

    def getTable(self,tableNode):
        thead = tableNode("thead")
        print(thead)
        heads = thead("th")
        ls = list()
        for i in range(len(heads)):
            ls.append(heads.eq(i).text())
        print(ls)
        tbody = tableNode("tbody")
        trs = tbody("tr")
        table = list()
        table.append(ls)
        for i in range(len(trs)):
            tr = trs.eq(i)
            tds = tr("td")
            item = list()
            for j in range(len(tds)):
                ele = tds.eq(j).text()
                item.append(ele)
            print(item)
            table.append(item)
        return table

    def parse_Page(self,response):
        dom = pq(response.body)
        tableNode = dom(".profile.container")(".row").eq(2)("table")
        table = self.getTable(tableNode)
        contract = {}
        heads = table[0]
        for j in range(1, len(table)):
            for k in range(0, len(table[0])):
                contract[heads[k]] = table[j][k]
            if(len(contract['Address']) > 42):
                contract['Address'] = contract['Address'][:42]
            request = scrapy.Request(self.code_url + contract['Address'] + '#code', headers=self.headers, callback=self.getContract)
            yield request

    def getContractSourceCode(self, dom, contractAddr):
        try:
            source_code = dom("#dividcode")("pre.js-sourcecopyarea").html()
        # re_h = re.compile('</?\w+[^>]*>')
        # source_code = re_h.sub('', source_code)
            source_code.replace('</?\w+[^>]*>', '')
            source_code.replace("&gt;", ">").replace("&lt;", "<")
            source_code.replace('&#13;', ' ')
            file_path = r'verified_contracts/' + contractAddr + ".sol"

            print(file_path)
            out = open(file_path, "wb+")
            out.write(source_code.encode("utf-8"))
            out.close()
        except Exception as e:
            print(e)

    def getContractAbi(self, dom, contractAddr):
        abi = dom("#dividcode")("#js-copytextarea2")
        if abi.text() is None or len(abi.text()) == 0:
            return None
        file_path = r'verified_contract_abis/' + contractAddr + ".abi"

        print(file_path)
        out = open(file_path, "w+")
        out.write(abi.text())
        out.close()
        # print(abi.text())
        return abi.text()

    def getContractBin(self, dom, contractAddr):
        bin = dom("#dividcode")("#verifiedbytecode2")
        if bin.text() is None or len(bin.text()) == 0:
            return None
        file_path = r'verified_contract_bins/' + contractAddr + ".bin"

        print(file_path)
        out = open(file_path, "w+")
        out.write(bin.text())
        out.close()
        # print(bin.text())
        return bin.text()

    def getContractConstructorParams(self, dom, contractAddr):
        pattern = re.compile('Constructor Arguments')
        if(len(pattern.findall(dom.text())) == 0):
            return None
        wordwraps = dom("pre.wordwrap")
        if len(wordwraps) < 4:
            return None
        constructor = wordwraps.eq(2)
        if constructor.text() is None or len(constructor.text()) == 0:
            return None
        file_path = r'verified_contract_constructorparams/' + contractAddr + ".constructorparams"
        print(file_path)
        out = open(file_path, "w+")
        txt = [constructor.text().split("-----Encoded View---------------")[0]]
        txt.extend(constructor.text().split("-----Encoded View---------------")[1].split("Arg"))
        txt = "\n".join(txt)
        out.write(txt)
        out.close()

    def getContractLibrary(self, dom, contractAddr):
        pattern = re.compile('Library Used')
        if(len(pattern.findall(dom.text())) == 0):
            return None
        number = 2
        pattern = re.compile('Constructor Arguments')
        if(len(pattern.findall(dom.text())) > 0):
            number = number +1
        wordwraps = dom("pre.wordwrap")
        if len(wordwraps) < 4:
            return None
        library = wordwraps.eq(number)
        if library.text() is None or len(library.text()) == 0:
            return None
        file_path = r'verified_contract_libraryparams/' + contractAddr + ".libraryparams"
        print(file_path)
        out = open(file_path, "w+")
        out.write(library.text())
        out.close()

    def getContract(self, response):
        print(response.url)
        Addr = (response.url).split('/')[-1]
        dom = pq(response.body)
        try:
            self.getContractSourceCode(dom, Addr)
            self.getContractAbi(dom, Addr)
            self.getContractBin(dom, Addr)
            self.getContractConstructorParams(dom, Addr)
            self.getContractLibrary(dom, Addr)
            with open(self.logfile,"a+") as f:
                f.write(str(datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))+','+response.url+'\n')
        except Exception as e:
            with open(self.errorfile,"a+") as f:
                f.write(str(datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))+','+response.url+str(e)+'\n')