#!/usr/bin/env python
import random
import requests
from lxml import html
import re
import json

USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
               'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
               ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) '
                'Chrome/19.0.1084.46 Safari/536.5'),
               ('Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46'
                'Safari/536.5'),)


def _request_page(link):
    return requests.get(link, headers={'User-Agent': random.choice(USER_AGENTS)})


# get the car description
brand_body_types_link = "http://www.kbb.com/jsdata/3.0.0.0_51577/_makesmodels?vehicleclass=UsedCar&yearid=2012"
response = _request_page(brand_body_types_link)
response_in_json = response.json()
urls = []
for brand_category in response_in_json:
    name = brand_category["Name"].replace(' ', '-')
    body_types = [body_type['Name'] for body_type in brand_category['Model']]
    urls_of_brand = ["http://www.kbb.com/{0}/{1}/{2}/categories/".format(name, body_type.replace(' ', '-'), "2012") for
                     body_type in body_types]
    urls.extend(urls_of_brand)
# print '\n'.join(map(str, urls))

# testing bmw links
bmw_links = [link for link in urls if "BMW" in link]
# print bmw_links
bmw_links = [bmw_links[0]]

choose_style_links = []
for bmw_link in bmw_links:
    result = _request_page(bmw_link)
    tree = html.fromstring(result.content)
    style_links_of_brand = ["http://www.kbb.com/{}".format(a.get('href')) for a in
                            tree.cssselect('div .mod-category-inner a')] or [bmw_link]
    choose_style_links.extend(style_links_of_brand)

option_pages = []
for choose_style_link in choose_style_links:
    result = _request_page(choose_style_link)
    tree = html.fromstring(result.content)
    option_links = ["http://www.kbb.com/{}".format(a.get('href')) for a in tree.cssselect('div .vehicle-styles-head a')]
    # remove the page that customize the body type
    regular_option_links = filter(lambda link: "compare-styles" not in link, option_links)
    option_pages.extend(regular_option_links)

print option_pages


def _construct_detail_page(option_link):
    temp_link = option_link.replace("options/", "")
    return temp_link + "&options=&mileage=57812&condition=excellent&pricetype=private-party&zipo="


detail_pages = map(_construct_detail_page, option_pages)

pattern = re.compile(ur'(?:\"values\": )({(?:\s|.)*?)(?:,\s+\"timAmount\")')


def _get_price_from_matched_text(content):
    parsed_json = json.loads(content)
    return parsed_json["privatepartyexcellent"]["price"]


for detail_page in detail_pages:
    result = requests.get(detail_page, headers={'User-Agent': random.choice(USER_AGENTS)},
                          cookies={'PersistentZipCode': '94089'})
    matched = pattern.search(result.content)
    if matched:
        print _get_price_from_matched_text(matched.group(1))

# task2. distribute version of request
