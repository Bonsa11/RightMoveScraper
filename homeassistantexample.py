from datetime import datetime, timedelta
import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv
import os

region_identifiers = {'Clifton Down Station': 'STATION%5E2195',  # Clifton Down Station
                      'Redlands Station': 'STATION%5E7640',  # Redlands Station
                      'Redlands Region': 'REGION%5E20676',  # Redlands Region
                      'Clifton Region': 'REGION%5E6574'  # Clifton Region
                      }


def get_url(identifier: str, page: int = 0, beds: tuple = (2, 2), price: tuple = (1000, 1500), radius: float = 0.25):
    """Generates URLs for Scraping"""
    min_bed, max_bed = beds
    min_price, max_price = price
    url = f'https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier={identifier}&index={page * 24}&maxBedrooms={max_bed}&minBedrooms={min_bed}&maxPrice={max_price}&minPrice={min_price}&radius={radius}&propertyTypes=&includeLetAgreed=false&mustHave=&dontShow=&furnishTypes=&keywords='

    return url


def format_date(date):
    if date == 'today':
        return datetime.now().strftime("%d/%m/%Y")
    elif date == 'yesterday':
        return (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
    else:
        return date


def send_home_assistant_notif():
    pass


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
            if titles[index] == 'Property':
                pass
            else:
                results.append({
                    'title': titles[index],
                    'address': addresses[index],
                    'description': descriptions[index],
                    'price': f'£{prices[index][1:]}',
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
    return parse(response.text)



def right_move_scraper(max_pages: int = 1):
    result_dict = {}
    for key, value in region_identifiers.items():
        for page in range(0, max_pages):
            try:
                url = get_url(value, page=page)
                result_dict[f'{key}-{page}'] = run(url)
            except Exception as e:
                print(f'page {page} for {key} probably doesnt exist')

    df = pd.DataFrame()
    for key, value in result_dict.items():
        for dict_ in value:
            tmp_df = pd.DataFrame.from_dict([dict_])
            tmp_df.columns = ['title', 'address', 'description', 'price', 'date', 'seller', 'image']
            df = pd.concat([df, tmp_df])

    df['date'] = df['date'].map(lambda x: datetime.strptime(x, '%d/%m/%Y').strftime('%Y-%m-%d'))
    df = df.drop_duplicates(subset=['image'])
    df = df.sort_values(by='date', ascending=False)

    df_old = pd.read_csv('rightmove.csv')
    if len(df_old[df_old['date'] == max(df_old['date'])]) == len(df[df['date'] == max(df['date'])]):
        print('no new properties found')
    else:
        send_home_assistant_notif()
        df.to_csv('rightmove.csv')

if __name__ == '__main__':
    right_move_scraper(5)