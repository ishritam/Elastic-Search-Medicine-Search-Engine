# import libraries
import warnings
warnings.filterwarnings("ignore")

# Try Block
try:
    from flask import app,Flask
    from flask_restful import Resource, Api, reqparse
    import elasticsearch
    from elasticsearch import Elasticsearch
    import datetime
    import concurrent.futures
    import requests
    import json
except Exception as e:
    print("Modules Missing {}".format(e))

# Flask app
app = Flask(__name__)
api = Api(app)

#------------------------------------------------------------------------------------------------------------
# Instantiate the new Elasticsearch connection:
es_header = es_header = [{'host': 'osso-7********75.us-east-1.bonsaisearch.net',
            'port': 443,
            'use_ssl': True,
            'http_auth': ('******', '*******')}]
NODE_NAME = 'my_med'
es = Elasticsearch(es_header)

#------------------------------------------------------------------------------------------------------------


class Controller(Resource):
    def __init__(self):
        self.query = parser.parse_args().get("query", None)
        self.baseQuery ={
            "_source": [],
            "size": 0,
            "min_score": 0.5,
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase_prefix": {
                                "name": {
                                    "query": "{}.".format(self.query)
                                }
                            }
                        }
                    ],
                    "filter": [],
                    "should": [],
                    "must_not": []
                }
            },
            "aggs": {
                "auto_complete": {
                    "terms": {
                        "field": "name.keyword",
                        "order": {
                            "_count": "desc"
                        },
                        "size": 8
                    }
                }
            }
        }

    def get(self):
        res = es.search(index=NODE_NAME, size=0, body=self.baseQuery)
        #print(res)
        return res


parser = reqparse.RequestParser()
parser.add_argument("query", type=str, required=True, help="query parameter is Required ")

api.add_resource(Controller, '/autocomplete')


if __name__ == '__main__':
    app.run(debug=True, port=4000)
