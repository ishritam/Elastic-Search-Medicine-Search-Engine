import scrapy
import re
import json
from pprint import pprint
from string import ascii_lowercase
import redis






class MgLVSpider(scrapy.Spider):
    #name of the spider
    name = 'mg_lv'
    clint = redis.Redis(host= "127.0.0.1", port=6379,charset="utf-8", decode_responses=True)
    
    #alpha = ascii_lowercase()
    allowed_domain = 'https://www.1mg.com'



    # start_urls = ['https://www.1mg.com/pharmacy_api_gateway/v4/drug_skus/by_prefix?'
    #         'prefix_term=l&page=20'
    #         '&per_page=30']

           # all_urls.append(start_urls)       
    def start_requests(self):
        alphas = list(ascii_lowercase)
        pages = [724,207, 664, 369, 299, 259, 230, 102, 145, 43, 122, 320, 438, 305, 330, 429, 31, 
                396, 384, 421, 71, 191, 53, 49, 16,197 ]


        start_urls= []
        for f, b in zip(alphas, pages):
            for i in range(1,b+1):
                start_url = f'https://www.1mg.com/pharmacy_api_gateway/v4/drug_skus/by_prefix?prefix_term={f}&page={i}&per_page=30'
                start_urls.append(start_url)
        
        for url in start_urls:
                    yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        result = json.loads(response.body)

        final_result = []
        for i in range(len(result['data']['skus'])):
            temp = {}
            temp["name"] = result['data']['skus'][i]['name']
            temp["price"] = result['data']['skus'][i]['price']
            temp["image_url"]= result['data']['skus'][i]['image_url']
            temp["type"] = result['data']['skus'][i]['type']
            temp["slug"] = self.allowed_domain +result['data']['skus'][i]['slug']
            temp["manufacturer_name"] = result['data']['skus'][i]['manufacturer_name']
            self.clint.lpush('urls', self.allowed_domain +result['data']['skus'][i]['slug'])
            final_result.append(temp)

        yield final_result
        # out_file = open("1mg_lv.json", "a") 
        # json.dump(final_result, out_file, indent = 6) 
        # out_file.close()

        #pprint(final_result)
