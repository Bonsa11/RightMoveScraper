from datetime import datetime, timedelta


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


if __name__ == '__main__':
    print(format_date('today'))
    print(format_date('yesterday'))
