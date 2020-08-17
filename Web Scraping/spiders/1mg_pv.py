import scrapy
import re
import json
from pprint import pprint
from string import ascii_lowercase
import redis

class MedLVSpider(scrapy.Spider):
    #name of the spider
    name = 'mg_pv'
    clint = redis.Redis(host= "127.0.0.1", port=6379,charset="utf-8", decode_responses=True)

    # #list of allowed domains
    allowed_domain = 'https://www.1mg.com'
    # def start_requests(self):
    #     start_urls =  ['https://www.1mg.com/drugs/calpol-650mg-tablet-74819','https://www.1mg.com/drugs/augmentin-625-duo-tablet-138629']
    #     for url in start_urls:
    #                 yield scrapy.Request(url=url, callback=self.parse)
        
    
    count = 0
    def start_requests(self):
        #alphas = list(ascii_lowercase)
        #pages = [722,207, 664, 368, 298, 258, 230, 102, 145, 43, 122, 319, 437, 305, 329, 428, 31, 
        #        395, 383, 420, 71, 191, 52, 49, 16,196 ]

        #poping = self.clint.rpop('urls')
        #start_urls= self.clint.lrange('urls',0,-1)
        start_urls = [self.clint.rpop('urls') for i in self.clint.lrange('urls',0,-1)]
        # for f, b in zip(alphas, pages):
        #     for i in range(1,b+1):
        #         start_url = f'https://www.1mg.com/pharmacy_api_gateway/v4/drug_skus/by_prefix?prefix_term={f}&page={i}&per_page=30'
        #         result = json.loads(response.body)
        #         start_urls.append(start_url)
        
        for url in start_urls:
            if url is not None:
                yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        try:
            script = response.xpath("//script[contains(., 'short_introduction')]/text()").extract_first()
            pattern = re.compile(r"window.__INITIAL_STATE__ = (\{.*?\});", re.MULTILINE | re.DOTALL)
            match = pattern.search(script)
            
            temp_item = {}
            
            if match:
                data = match.group(1)
                data = json.loads(data)
                #md.append(data)
                

                temp_item['name'] = data['drugPageReducer']['data']['meta_data']['heading_tag']
                temp_item['price'] = data['pdpDynamicReducer']['data']['price']
                temp_item['pack_size'] = data['pdpDynamicReducer']['data']['pack_size']

                temp_item['Uses'] = [i['name'] for i in data['drugPageReducer']['data']['composition']['uses'][0]['values']]
                
                #Intro_0
                if len(data['drugPageReducer']['data']['composition']['short_introduction']) > 0:
                    temp_item['intro_0'] = data['drugPageReducer']['data']['composition']['short_introduction'][0]
                else:
                    temp_item['intro_0'] = None

                #Intro_1
                #temp_item['intro_1'] = data['drugPageReducer']['data']['composition']['uses'][0]['display_text']
                if len(data['drugPageReducer']['data']['composition']['introduction']) > 0:
                    temp_item['intro_1'] = data['drugPageReducer']['data']['composition']['introduction'][0]['display_text']
                else:
                    temp_item['intro_1'] = None

                #How to use?
                if 'how_to_take' in data['drugPageReducer']['data']['composition']:
                    for  i in data['drugPageReducer']['data']['composition']['how_to_take']:
                        temp_item['How to use?'] = i['display_text']
                else:
                    temp_item['How to use?'] =None
            
                if 'mechanism_of_action' in data['drugPageReducer']['data']['composition']:
                    for i in data['drugPageReducer']['data']['composition']['mechanism_of_action']:
                        if len(i)>0:
                            temp_item['How it works?'] = i['display_text']
                        else:
                            temp_item['How to works?'] =None
                else:
                    temp_item['How to works?'] =None
                #temp_item['How it works?'] = data['drugPageReducer']['data']['composition']['mechanism_of_action'][0]['display_text']


                #Quick Tips
                if 'expert_advice' in data['drugPageReducer']['data']['composition']:
                    for i in data['drugPageReducer']['data']['composition']['expert_advice']:
                        if len(i)>0:
                    #if 'display_text' in data['drugPageReducer']['data']['composition']['expert_advice']:
                            temp_item['expert_advice'] = i['display_text']
                        else:
                            temp_item['expert_advice'] = None
                else:
                    temp_item['expert_advice'] = None
                
                #safety_advice
                final_safety_advice = []
                safety_advice = data['drugPageReducer']['data']['warnings']['values']
                for i in safety_advice:
                    #print(i['display_text'])
                    temp_safety = {}
                    temp_safety['0'] = i['key']
                    temp_safety['1'] = i['description']
                    final_safety_advice.append(temp_safety)    
                        
                temp_item['safety_advice'] = final_safety_advice


                #side_effects
                temp_item['side_effects'] = [i['values'] for i in data['drugPageReducer']['data']['composition']['side_effects'][0]['values']]
                

                #faqs
                if 'faqs' in data['drugPageReducer']['data']['composition']:
                    final_faqs = []
                    for i in data['drugPageReducer']['data']['composition']['faqs']:
                    # if 'values' in data['drugPageReducer']['data']['composition']['faqs']:
                        if len(i)>0:
                            for j in i['values']:
                                temp_faq = {}
                                temp_faq['0'] = j['question']
                                temp_faq['1'] = j['answer']
                                
                                final_faqs.append(temp_faq)
                        else:
                            temp_item['faqs'] = None
                            
                    temp_item['faqs'] = final_faqs

                else:
                    temp_item['faqs'] = None
                #temp_item['faqs'] = data['drugPageReducer']['data']['composition']['faqs'][0]['values']

                ###Images
                #temp_item['Images'] = [i for i in data["drugPageReducer"]["data"]["sku"]["images"]]
                if 'images' in data["drugPageReducer"]["data"]["sku"]:
                    if data["drugPageReducer"]["data"]["sku"]['images'] != None:
                        for i in data["drugPageReducer"]["data"]["sku"]["images"]:
                            #temp_img = {}
                            temp_item['Images'] = i
                    else:
                        temp_item['Images'] = None

                else:
                    temp_item['Images'] = None

                temp_item['lv_url'] = response.url
                temp_item['url'] = self.allowed_domain + data['drugPageReducer']['data']['schema']['drug']['url']
                print(self.count)
                self.count+=1
                yield temp_item
        
        except Exception as e:
            print(response.url)
            print(e)
