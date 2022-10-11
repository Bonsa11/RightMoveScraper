import requests
from bs4 import BeautifulSoup
import csv
import os

from utility import format_date


def fetch(url):
    # print('HTTP GET request to URL: %s' % url, end='')
    response = requests.get(url)
    # print(' | Status code: %s' % response.status_code)

    return response


def parse(html):
    content = BeautifulSoup(html, 'lxml')

    titles = [title.text.strip() for title in content.findAll('h2', {'class': 'propertyCard-title'})]
    # (f'there is {len(titles)} titles')
    print(f'there are {len(titles)} properties found')

    addresses = [address['content'] for address in content.findAll('meta', {'itemprop': 'streetAddress'})]
    # (f'there is {len(addresses)} addresses')

    descriptions = [description.text for description in
                    content.findAll('span', {'data-test': 'property-description'})]
    # (f'there is {len(descriptions)} descriptions')

    prices = [price.text.strip() for price in content.findAll('span', {'class': 'propertyCard-priceValue'})]
    # (f'there is {len(prices)} prices')

    dates = [format_date(date.text.split(' ')[-1]) for date in
             content.findAll('span', {'class': 'propertyCard-branchSummary-addedOrReduced'})]
    # (f'there is {len(dates)} dates')

    sellers = [seller.text.split('by')[-1].strip() for seller in
               content.findAll('span', {'class': 'propertyCard-branchSummary-branchName'})]
    # (f'there is {len(sellers)} sellers')

    images = [image['src'] for image in content.findAll('img', {'itemprop': 'image'})]
    # (f'there is {len(images)} images')

    results = []
    for index in range(0, len(titles)):
        try:
            results.append({
                'title': titles[index],
                'address': addresses[index],
                'description': descriptions[index],
                'price': prices[index],
                'date': dates[index],
                'seller': sellers[index],
                'image': images[index],
            })
        except Exception as e:
            print(titles[index], e)

    return results


def read_csv():
    try:
        with open('rightmove_test.csv', mode="r") as csv_file:  # "r" represents the read mode
            return [r for r in csv.reader(csv_file)]  # this is the reader object
    except Exception as e:
        print('no file to read')


def to_csv(results):
    existing = None
    if os.path.exists('rightmove_test.csv'):
        existing = read_csv()

    with open('rightmove_test.csv', 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=results[0].keys())
        writer.writeheader()

        for row in results:
            if existing:
                if row not in existing:
                    writer.writerow(row)
            else:
                writer.writerow(row)

        print('Stored results to "rightmove_test.csv"')


def run(url):
    response = fetch(url)
    results = parse(response.text)
    to_csv(results)


if __name__ == '__main__':
    url = 'https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=STATION%5E2195&index=0&maxBedrooms=2&minBedrooms=2&maxPrice=1500&minPrice=1000&radius=1.0&propertyTypes=&includeLetAgreed=false&mustHave=&dontShow=&furnishTypes=&keywords='
    run(url)
