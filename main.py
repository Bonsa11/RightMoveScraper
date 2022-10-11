from scraper import run
from utility import get_url
from config import region_identifiers


def main(max_pages: int = 0):
    for key, value in region_identifiers.items():
        print(f'looking for properties around the {key}')
        if max_pages == 0:
            run(get_url(value))
        else:
            for page in range(0, max_pages):
                try:
                    url = get_url(value, page=page)
                    print(url)
                    run(url)
                except Exception as e:
                    print(f'page {page} for {key} probably doesnt exist')


if __name__ == '__main__':
    main()
