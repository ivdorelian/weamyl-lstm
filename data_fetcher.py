import os.path

import requests
from bs4 import BeautifulSoup
from joblib import Parallel, delayed

class DataFetcher:

    DATA_FOLDER = 'data'

    def __get_tds(self, url):
        html = requests.get(url).content
        soup = BeautifulSoup(html, 'html.parser')
        return soup.find_all('td')

    def get_day(self, url):
        for td in self.__get_tds(url):
            anchor = td.find('a')
            if anchor and '.nc' in anchor['href']:
                nc_filename = anchor.tt.text
                to_download = url\
                    .replace('catalog.html', nc_filename)\
                    .replace('/catalog/', '/fileServer/')
                nc_file_data = requests.get(to_download)
                full_path = os.path.join(self.DATA_FOLDER, nc_filename)
                with open(full_path, 'wb') as f:
                    f.write(nc_file_data.content)
                print('Saved:', nc_filename)
                file_sz = os.path.getsize(full_path)
                if file_sz / 1024 / 1024 < 3:
                    with open('log.txt', 'a+') as f:
                        f.write(f'{nc_filename} seems to be too small!\n')


    def get_month(self, url):

        def handle_td(td):
            anchor = td.find('a')
            if anchor:
                print(f'--- Getting {anchor["href"]}:')
                day_url = url.replace('catalog.html', anchor['href'])
                self.get_day(day_url)

        Parallel(n_jobs=4)(delayed(handle_td)(td) for td in self.__get_tds(url))
