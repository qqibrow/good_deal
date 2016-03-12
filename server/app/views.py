from app import app
import redis
import json

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/vehicle_price/<brand>')
def get_all_vehicle_of_brand(brand):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    results = r.hgetall(brand)
    results_in_json = json.dumps(results)
    return results_in_json


