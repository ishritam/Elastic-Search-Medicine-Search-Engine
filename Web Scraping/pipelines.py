# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class Mg1Pipeline:
    def __init__(self):
        self.conn = pymongo.MongoClient('localhost',27017)

        db = self.conn['1mg']
        self.collection = db['pv'] 


    def process_item(self, item, spider):
        self.collection.insert(item)
        return item
