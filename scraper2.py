import requests
from bs4 import BeautifulSoup
import csv
import os
import re

from utility import format_date


def fetch(url):
    response = requests.get(url)

    return response


def get_links(html):
    content = BeautifulSoup(html, 'lxml')
    urls = [url.get('href') for url in content.findAll('a')]  # , {'class': 'propertyCard-link property-card-updates'})]
    links = [url for url in urls if re.match('^/properties.*$', str(url))]

    return links


def parse(link):
    url = f'https://www.rightmove.co.uk{link}'
    html = fetch(url).text
    content = BeautifulSoup(html, 'lxml')

    titles = [title['content'] for title in content.findAll('meta', {'item-prop': 'name'})]
    addresses = [address['content'] for address in content.findAll('hq', {'itemprop': 'streetAddress'})]
    urls = [url.get('href') for url in content.findAll('a')]  # , {'class': 'propertyCard-link property-card-updates'})]
    links = [url for url in urls if re.match('^/properties.*$', str(url))]
    descriptions = [description.text for description in
                    content.findAll('span', {'data-test': 'property-description'})]
    prices = [price.text.strip() for price in content.findAll('span', {'class': 'propertyCard-priceValue'})]
    dates = [format_date(date.text.split(' ')[-1]) for date in
             content.findAll('span', {'class': 'propertyCard-branchSummary-addedOrReduced'})]
    sellers = [seller.text.split('by')[-1].strip() for seller in
               content.findAll('span', {'class': 'propertyCard-branchSummary-branchName'})]
    images = [image['src'] for image in content.findAll('img', {'itemprop': 'image'})]

    results = []
    for index in range(0, len(titles)):
        try:
            if titles[index] == 'Property':
                pass
            else:
                results.append({
                    'title': titles[index],
                    'address': addresses[index],
                    'links': links[index],
                    'description': descriptions[index],
                    'price': f'£{prices[index][1:]}',
                    'date': dates[index],
                    'seller': sellers[index],
                    'image': images[index],
                })
        except Exception as e:
            print(titles[index], e)

    return results


def run(url):
    response = fetch(url)
    links = get_links(response.text)

    results = []
    for link in links:
        try:
            results.append(parse(link))
        except Exception as e:
            pass

    return results


if __name__ == '__main__':
    url = 'https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=STATION%5E2195&index=0&maxBedrooms=2&minBedrooms=2&maxPrice=1500&minPrice=1000&radius=1.0&propertyTypes=&includeLetAgreed=false&mustHave=&dontShow=&furnishTypes=&keywords='
    run(url)
