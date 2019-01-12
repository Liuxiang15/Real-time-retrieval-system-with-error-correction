# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from TsinghuaNews.settings import mongo_host,mongo_port,mongo_db_name,mongo_db_collection
from scrapy.exceptions import DropItem

class TsinghuanewsPipeline(object):
    def __init__(self):
        host = mongo_host
        port = mongo_port
        dbname = mongo_db_name
        sheetname = mongo_db_collection
        client = pymongo.MongoClient(host=host, port=port)
        mydb = client[dbname]
        self.post = mydb[sheetname]

    def process_item(self, item, spider):
        item_dict = dict(item)
        if not item_dict:   #判断是否为空
            raise DropItem("数据错误!")
        for data in self.post.find():
            if item_dict["title"] == data["title"] or item_dict["url"] == data["url"]:
                raise DropItem("网页数据重复!")
        new_id = self.post.insert(item_dict)

            