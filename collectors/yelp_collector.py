"""
Given a url address an ouput csv file, appends to the output file a line
containing the scraped url, the name of the business, and whether they are
wheelchair accessible ("Yes"), they aren't ("No"), or the information is
unavailable ("NA").
"""

from lxml import html
import requests
import argparse
import csv


def parse(url):
    # url = "https://www.yelp.com/biz/frances-san-francisco"
    response = requests.get(url).text
    parser = html.fromstring(response)
    print("Parsing the page")
    raw_name = parser.xpath("//h1[contains(@class,'page-title')]//text()")
    details_table = parser.xpath("//div[@class='short-def-list']//dl")

    for details in details_table:
        raw_description_key = details.xpath('.//dt//text()')
        raw_description_value = details.xpath('.//dd//text()')
        description_key = ''.join(raw_description_key).strip()
        description_value = ''.join(raw_description_value).strip()
        # info.append({description_key:description_value})
        if description_key == 'Wheelchair Accessible':
            info = description_value
            break
    else:
        info = "NA"

    name = ''.join(raw_name).strip()

    return url, name, info


def write_data_to_csv(data, filename):
    with open(filename, 'a') as fl:
        writer = csv.writer(fl)
        writer.writerow(data)


if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--url', help = 'yelp business url')
    argparser.add_argument('--output', help = 'output csv')
    args = argparser.parse_args()
    url = args.url
    scraped_data = parse(url)
    write_data_to_csv(scraped_data, args.output)
