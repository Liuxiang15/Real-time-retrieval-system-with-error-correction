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
    name = 'THUNewsSpider-1245'
    allowed_domains = ['news.tsinghua.edu.cn']
    count = 0

    # 本函数是针对中文网页第1245栏目第一级目录进行爬取
    def start_requests(self):
        url_list_type = [9648, 10303, 9650, 9652]
        page_num_list_type = [39, 479, 329, 16]
        for index, i in enumerate(url_list_type):
            for j in range(2, page_num_list_type[index]+1):
                yield scrapy.Request(
                    url =  'http://news.tsinghua.edu.cn/publish/thunews/{}/index_{}.html'.format(i, j),
                    callback = self.get_urls
                )

    # 本函数是针对中文网页第1245栏目第一级目录进行解析
    def get_urls(self, response):
        url_list = response.selector.xpath('//section[1]/ul/li/figure/figcaption/a/@href').extract()
        domain_name = 'http://news.tsinghua.edu.cn'
        for path in url_list:
            yield scrapy.Request(
                url=domain_name + path,
                callback=lambda response, url=domain_name+path:self.parse(response, url)
            )

    # 本函数是针对中文网页第1245栏目网页进行解析
    def parse(self, response, url):
        # print("当前处理的url是"+url)
        news_item = TsinghuanewsItem()
        news_item["url"] = url
        try:
            news_item["title"] = response.selector.xpath("//title/text()").extract_first()
            keywords = response.selector.xpath('//meta[@name="keywords"]/@content').extract_first()
            if keywords:
                news_item["keywords"]  = keywords.split(' ')[0]
            else:
                return
            print("关键词是：")
            print(news_item["keywords"])
            dates = response.selector.xpath('//div[@class="articletime"]/text()').extract_first()
            datestr_list = []
            if dates:
                datestr_list = dates.split(' ')
            else:
                return
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
        except: return


