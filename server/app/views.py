from app import app
import redis
import json
from flask import render_template

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/typeahead/<brand>')
def get_typeahead(brand):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    results = r.hgetall(brand)

    # Turn results to a list.
    results_in_json = json.dumps(results.keys())
    names = []
    for r in results_in_json:
        a = json.loads(r)
        names.append(a["model"])
    return names

@app.route('/vehicle_price/<brand>')
def get_all_vehicle_of_brand(brand):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    results = r.hgetall(brand)
    results_in_json = json.dumps(results)
    return results_in_json


