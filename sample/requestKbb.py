#!/usr/bin/env python
import random
import requests
from lxml import html
import re
import json
import redis
from collections import namedtuple
import logging
import time
import os.path

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

fname = 'data.txt'
if not os.path.isfile(fname):
    obj = open(fname, 'wb')
else:
    print "file %s already exists." % fname
    exit(-1)

VehicleIdentifier = namedtuple("VehicleIdentifier", "brand year body_type")

def categories_page(vehicle):
    return "http://www.kbb.com/{0}/{1}/{2}/categories/".format(vehicle.brand, vehicle.body_type, vehicle.year)


USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
               'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
               ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) '
                'Chrome/19.0.1084.46 Safari/536.5'),
               ('Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46'
                'Safari/536.5'),)


def _request_page(link):
    return requests.get(link, headers={'User-Agent': random.choice(USER_AGENTS)})

# the start of time of all
start_time = time.time()

# get the car description
year = 2012
brand_body_types_link = "http://www.kbb.com/jsdata/3.0.0.0_51577/_makesmodels?vehicleclass=UsedCar&yearid=%d" % year
response = _request_page(brand_body_types_link)
response_in_json = response.json()

# Get all kinds of Vehicle Identifiers.
vehicles = []
for brand_category in response_in_json:
    name = brand_category["Name"].replace(' ', '-')
    body_types = [body_type['Name'] for body_type in brand_category['Model']]
    vehicles_of_this_brand = [VehicleIdentifier(brand=name, year=year, body_type=body_type.replace(' ', '-')) for
                              body_type in body_types]
    vehicles.extend(vehicles_of_this_brand)

end_time = time.time()
logging.debug("fetched %d vehicles info in %d seconds" % (len(vehicles), start_time - end_time))

# testing bmw links
# selected_vehicles = [v for v in vehicles if "BMW" in v.brand]
# selected_vehicles = [selected_vehicles[0]]
selected_vehicles = vehicles

def _construct_detail_page(option_link):
    temp_link = option_link.replace("options/", "")
    return temp_link + "&options=&mileage=57812&condition=excellent&pricetype=private-party&zipo="

option_pages = []

link_to_vehicle = {}
for vehicle in selected_vehicles:
    vehicle_categories_page = categories_page(vehicle)
    result = _request_page(vehicle_categories_page)
    tree = html.fromstring(result.content)
    style_links_of_brand = ["http://www.kbb.com{}".format(a.get('href')) for a in
                            tree.cssselect('div .mod-category-inner a')] or [vehicle_categories_page]

    for choose_style_link in style_links_of_brand:
        result = _request_page(choose_style_link)
        tree = html.fromstring(result.content)
        option_links = ["http://www.kbb.com/{}".format(a.get('href')) for a in tree.cssselect('div .vehicle-styles-head a')]
        # remove the page that customize the body type
        regular_option_links = filter(lambda link: "compare-styles" not in link, option_links)
        option_pages.extend(regular_option_links)

        # add link to vehicle connection
        for option_link in regular_option_links:
            s = _construct_detail_page(option_link)
            link_to_vehicle[s] = vehicle
    logging.debug("finished getting all the option_links of %s", vehicle.brand)

detail_pages = map(_construct_detail_page, option_pages)

pattern = re.compile(ur'(?:\"values\": )({(?:\s|.)*?)(?:,\s+\"timAmount\")')


def _get_price_from_matched_text(content):
    parsed_json = json.loads(content)
    return parsed_json["privatepartyexcellent"]["price"]

r = redis.StrictRedis(host='localhost', port=6379, db=0)
def write_to_redis(vehicle, model, matched_text_in_detail_page):
    price = _get_price_from_matched_text(matched_text_in_detail_page)
    key_in_dict = {'brand': vehicle.brand, 'year': vehicle.year, 'body_type': vehicle.body_type, 'model': model}
    key = json.dumps(key_in_dict)
    value = price
    # Write brand name lowercase map into redis.
    r.hset(vehicle.brand.lower(), key, value)


def append_to_file(vehicle, model, matched_text_in_detail_page):
    content = json.loads(matched_text_in_detail_page)
    key_in_dict = {'brand': vehicle.brand, 'year': vehicle.year, 'body_type': vehicle.body_type, 'model': model, 'value': content}
    json.dump(key_in_dict, obj)
    obj.write('\n')


for detail_page in detail_pages:
    result = requests.get(detail_page, headers={'User-Agent': random.choice(USER_AGENTS)},
                          cookies={'PersistentZipCode': '94089'})
    matched = pattern.search(result.content)
    extract_model_pattern = re.compile(ur'(?:' + str(year) + ur'\/)(.*?)(?:\/\?vehicleid)')
    model = extract_model_pattern.search(detail_page)
    if matched:
        append_to_file(link_to_vehicle[detail_page], model.group(1), matched.group(1))
        logging.debug("written detailed page %s", detail_page)
obj.close()

# task2. distribute version of request
