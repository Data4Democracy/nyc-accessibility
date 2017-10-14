import datetime

from bs4 import BeautifulSoup
import dataset
from dateutil.parser import parse
import requests


API_ENDPOINT = 'http://web.mta.info/developers/data/nyct/nyct_ene.xml'


def get_outages(url):
    response = requests.get(url)
    return response


def parse_xml(xml):
    parsed_xml = BeautifulSoup(xml, 'lxml-xml')
    return parsed_xml


def map_outage(outage):
    service_outage = {}
    for element in outage:
        service_outage[element.name] = element.text.strip()
        if element.name in ['estimatedreturntoservice', 'outagedate']:
            service_outage[element.name] = parse(service_outage[element.name])
    return service_outage


def save(service_outage):
    db = dataset.connect('sqlite:///outage_scraper.sqlite')
    table = db['outage']
    service_outage['created_at'] = datetime.datetime.utcnow()
    table.insert(service_outage)


def main():
    response = get_outages(API_ENDPOINT)
    if response.ok:
            outages = parse_xml(response.text)
    else:
        print("Not ok")
        return

    for outage in outages.NYCOutages.find_all('outage'):
        service_outage = map_outage(outage)
        save(service_outage)
        print(service_outage)


if __name__ == '__main__':
    main()
