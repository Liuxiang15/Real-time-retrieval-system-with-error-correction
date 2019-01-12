# -*- coding: utf-8 -*-
import scrapy
from TsinghuaNews.items import TsinghuanewsItem
from scrapy.selector import Selector

import html2text
h = html2text.HTML2Text()
h.ignore_links = False
h.ignore_images = True

class ThunewsspiderSpider(scrapy.Spider):
    #爬虫名不能和项目名重复
    name = 'ETHUNewsSpider'
    allowed_domains = ['news.tsinghua.edu.cn']
    count = 0

    # 本函数是针对英文网页第1246789栏目第1级目录进行相应爬取
    def start_requests(self):
        url_list = [9670, 9671, 9673, 9675, 9676, 9677, 9678]
        page_num_list = [68, 249, 109, 24, 36, 18, 136]
        for index, i in enumerate(url_list):
            for j in range(2, page_num_list[index] + 1):
                yield scrapy.Request(
                    url='http://news.tsinghua.edu.cn/publish/thunewsen/{}/index_{}.html'.format(i, j),
                    callback=self.get_eurls
                )

    # 本函数是针对英文网页第1246789栏目第1级目录进行相应解析
    def get_eurls(self, response):
        #定义一个列表，分别统计九种英语新闻的对应的页面数
        eurl_list = response.selector.xpath('//ul[@class="txtlist clearfix"]/li/div/a/@href').extract()
        domain_name = 'http://news.tsinghua.edu.cn'
        for path in eurl_list:
            yield scrapy.Request(
                url=domain_name+path,
                callback=lambda response, url=domain_name+path:self.e_parse(response, url)
            )

    # 本函数是针对英文网页第1246789栏目网页进行相应解析
    def e_parse(self, response, url):
        enews_item = TsinghuanewsItem()
        enews_item["url"] = url
        enews_item["title"] = response.selector.xpath("//h1/text()").extract_first()
        enews_item["keywords"] = ""
        date_str = url.replace("http://news.tsinghua.edu.cn/publish/thunewsen","")[11:19]
        date_list = []
        #分别添加年月日作为数组元素
        date_list.append(date_str[0:4])
        date_list.append(date_str[4:6])
        date_list.append(date_str[6:8])
        date = date_list[0] + "年" + date_list[1] + "月" + date_list[2] + "日"
        enews_item["date"] = date
        paragraph_list = response.selector.xpath('//article[1]/p').extract()
        content = ""
        for index, paragraph in enumerate(paragraph_list):
            paragraph = h.handle(paragraph)
            paragraph = paragraph.replace("\ue863", "")  # 去除乱码
            paragraph = paragraph.replace("\n", "")      # 去除换行符
            content += paragraph
            if (paragraph == ""):
                continue
            content += "\n"                             # 加换行符
        enews_item["content"] = content
        self.count += 1
        print("成功解析的英文网页数量为："+str(self.count))
        yield enews_item

   
