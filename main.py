import pandas as pd
from datetime import datetime
import os
from sys import platform

from scraper import run
from utility import get_url, send_home_assistant_notif
from config import region_identifiers


def main(max_pages: int = 1):
    if platform == "linux" or platform == "linux2":
        csv_path = '/tmp/rightmove.csv'
    elif platform == "darwin":
        csv_path = '/tmp/rightmove.csv'
    elif platform == "win32":
        csv_path = 'rightmove.csv'

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

    if os.path.exists(csv_path):
        df_old = pd.read_csv(csv_path)
        if len(df_old[df_old['date'] == max(df_old['date'])]) == len(df[df['date'] == max(df['date'])]):
            print('no new properties found')
        else:
            send_home_assistant_notif()
            df.to_csv(csv_path)
    else:
        send_home_assistant_notif()
        df.to_csv(csv_path)


if __name__ == '__main__':
    main(5)