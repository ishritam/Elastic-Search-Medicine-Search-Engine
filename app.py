#import libraries
import warnings
warnings.filterwarnings("ignore")
from flask import Flask
from flask import request,redirect,render_template,session, jsonify
import requests
import base64
import re
# import requests module 
import requests


app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template("home.html")


@app.route('/pipe', methods=["GET", "POST"])
def pipe():
    data = request.form.get("data")
    payload = {}
    headers= {}
    #api for match phrase prefix query
    url = " https://osso-*******.herokuapp.com/autocomplete?query="+str(data)
    #url = "http://127.0.0.1:4000/autocomplete?query="+str(data)
    response = requests.request("GET", url, headers=headers, data = payload)
    return response.json()

@app.route('/submit', methods=["GET", "POST"])
#@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def submit():
    name_name = request.form.get("data")
    
    headers = {
        'Content-Type': 'application/json',
    }

    data = '{ "query": {"bool": { "must": [ { "match_phrase_prefix": { "name": { "query":"'+str(name_name)+'" } } } ], "filter": [], "should": [], "must_not": [] }} }'
    response = requests.post('https://******:******@osso-7964*******5.us-east-1.bonsaisearch.net:443/my_med/_search', headers=headers, data=data)
    resp = response.json()
    #return resp
    # Making a get request 
    #response = requests.get(url) 
    #resp = response.json()
    temp = {}
    #return resp
    if len(resp['hits']['hits']) > 0:
        for k in resp['hits']['hits']:
            temp['name'] = k['_source']['name']
            
            temp['Clean_Uses'] = k['_source']['Clean_Uses']
            temp['Clean_intro_0'] = k['_source']['Clean_intro_0']
            temp['Clean_intro_1'] = k['_source']['Clean_intro_1']
            temp['price'] = k['_source']['price']
            
            temp['Clean_expert_advice'] = k['_source']['Clean_expert_advice']
            
            line = k['_source']['Clean_side_effects']
            temp['Clean_side_effects'] = re.sub(r'(?<=[.,])(?=[^\s])', r' ', line)
            temp['pack_size'] = k['_source']['pack_size']
    
    else:
        with open('input.txt', 'a') as f:
                f.write(f'{name_name}\n')
        return render_template('no_data_rendtem.html')

    return render_template('rendtem.html', value_0 = temp['name'],value_1 = temp['Clean_Uses'],value_2 = temp['Clean_intro_0'], value_3=temp['Clean_intro_1'],value_4 = temp['pack_size'],value_5=temp['price'],value_6=temp['Clean_expert_advice'],value_7 = temp['Clean_side_effects'])

if __name__ == "__main__":
    app.run(debug=True, port=5000)
