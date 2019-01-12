# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TsinghuanewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #当前四个字段分别为标题，关键词，日期，正文内容，网页标签tag和作者author可以根据网页情况后续添加
    title = scrapy.Field()
    keywords = scrapy.Field()
    date = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()

