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

    all_keys = results.keys()
    # Turn results to a list.
    names = []
    for r in all_keys:
        vehicle_description = json.loads(r)
        name = "%s-%s-%s-%d" % (vehicle_description['brand'], vehicle_description['body_type'], vehicle_description['model'], vehicle_description['year'])
        names.append(name)
    return json.dumps(names)

@app.route('/vehicle_price/<brand>')
def get_all_vehicle_of_brand(brand):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    results = r.hgetall(brand)
    results_in_json = json.dumps(results)
    return results_in_json


