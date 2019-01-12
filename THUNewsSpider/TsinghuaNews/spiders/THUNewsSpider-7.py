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
    name = 'THUNewsSpider-7'
    allowed_domains = ['news.tsinghua.edu.cn']
    count = 0

    # 本函数是针对中文网页第7栏目清华人物第1级目录进行相应爬取
    def start_requests(self):
        max_page_num = 13
        for j in range(2, max_page_num + 1):
            yield scrapy.Request(
                url='http://news.tsinghua.edu.cn/publish/thunews/9656/index_{}.html'.format(j),
                callback=self.get_urls
            )

    # 本函数是针对中文网页第7栏目清华人物第1级目录进行解析
    def get_urls(self, response):
        url_list = response.selector.xpath('//li/figure/div/figcaption/a/@href').extract()
        domain_name = 'http://news.tsinghua.edu.cn'
        for path in url_list:
            yield scrapy.Request(
                url=domain_name + path,
                callback=lambda response, url=domain_name + path: self.parse(response, url)
            )

    # 本函数是针对中文网页第7栏目清华人物网页进行解析
    def parse(self, response, url):
        #print(response.text)
        news_item = TsinghuanewsItem()
        news_item["url"] = url
        # try:
        news_item["title"] = response.selector.xpath("//title/text()").extract_first()
        keywords = response.selector.xpath('//meta[@name="keywords"]/@content').extract_first()
        if keywords:
            news_item["keywords"] = keywords.split(' ')[0]
        else:
            # raise DropItem("解析网页出错")
            return
        print("关键词是：")
        print(news_item["keywords"])
        datestr_list = response.selector.xpath('//div[@class="articletime"]/text()').extract_first().split(' ')
        day = datestr_list[0]
        time = datestr_list[1].split("\u3000")[0]
        news_item["date"] = day + time
        #单纯的以p标签作为识别
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

            

