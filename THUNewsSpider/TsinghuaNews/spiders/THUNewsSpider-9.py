# -*- coding: utf-8 -*-
import scrapy
from TsinghuaNews.items import TsinghuanewsItem
from scrapy.selector import Selector
from scrapy.exceptions import DropItem

import html2text
h = html2text.HTML2Text()
h.ignore_links = False
h.ignore_images = True

class ThunewsspiderSpider(scrapy.Spider):
    #爬虫名不能和项目名重复
    name = 'THUNewsSpider-9'
    allowed_domains = ['news.tsinghua.edu.cn']
    count = 0

    # 本函数是针对中文网页第9栏目专题新闻第1级目录进行相应爬取
    def start_requests(self):
        max_page_num = 32
        for j in range(2, max_page_num+1):
            yield scrapy.Request(
                url =  'http://news.tsinghua.edu.cn/publish/thunews/9655/index_{}.html'.format(j),
                callback = self.get_directory
            )


    #本函数是针对中文网页第9栏目专题新闻第1级目录进行相应解析的
    def get_directory(self, response):
        url_list = response.selector.xpath('//section[@class="colunm1"]/ul/li/div/h3/a/@href').extract()
        domain_name = 'http://news.tsinghua.edu.cn'
        max_spe_num = 10                                #默认每个专题下最多的页数是10
        for index, path in enumerate(url_list):
            for i in range(2, max_spe_num):
                str_index = str("_{}.html".format(i))
                new_url = domain_name + url_list[index]
                new_url = new_url[:-5] + str_index
                yield scrapy.Request(
                    url=new_url,
                    callback=self.get_speurls
                )

    # 本函数是针对中文网页第9栏目专题新闻第2级目录进行相应解析的
    def get_speurls(self, response):
        speurl_list = response.selector.xpath('//ul[@class="timenewslist withtopborder"]/li/div/h3/a/@href').extract()
        domain_name = 'http://news.tsinghua.edu.cn'
        for path in speurl_list:
            yield scrapy.Request(
                url=domain_name+path,
                callback=lambda response, url=domain_name+path:self.parse(response, url)
            )

    # 本函数是针对中文网页第9栏目专题新闻网页进行相应解析的
    def parse(self, response, url):
        news_item = TsinghuanewsItem()
        news_item["url"] = url
        news_item["title"] = response.selector.xpath("//title/text()").extract_first()
        keywords = response.selector.xpath('//meta[@name="keywords"]/@content').extract_first()
        if keywords:
            news_item["keywords"] = keywords.split(' ')[0]
        else:
            return
        datestr_list = response.selector.xpath('//div[@class="articletime"]/text()').extract_first().split(' ')
        day = datestr_list[0]
        time = datestr_list[1].split("\u3000")[0]
        news_item["date"] = day + time
        paragraph_list = ""
        if("组图" in news_item["title"] or "图片传真" in news_item["title"]):
            paragraph_list = response.selector.xpath('//article[ @class ="article"][1]').extract()
        else:
            paragraph_list = response.selector.xpath('//article[@class="article"][1]/p').extract()

        content = ""
        for index, paragraph in enumerate(paragraph_list):
            paragraph = h.handle(paragraph)
            paragraph = paragraph.replace("\ue863", "")  # 去除乱码
            paragraph = paragraph.replace("\n", "")      #去除换行符
            if (paragraph == ""):
                continue
            content += paragraph
            content += "\n"                              # 加换行符
        news_item["content"] = content
        if news_item["content"] == "" or news_item["date"] == "" or news_item["keywords"] == "":
            print("提取正文、日期、关键词出错")
            return
        self.count += 1
        print("成功解析的中文网页数量为：" + str(self.count))
        yield news_item
            

