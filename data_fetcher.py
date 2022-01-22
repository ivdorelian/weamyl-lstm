import os.path

import requests
from bs4 import BeautifulSoup


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
                nc_file_data = requests.get(url.replace('catalog', 'fileServer') + nc_filename)
                with open(os.path.join(self.DATA_FOLDER, nc_filename), 'wb') as f:
                    f.write(nc_file_data.content)
                print('Saved:', nc_filename)

    def get_month(self, url):
        for td in self.__get_tds(url):
            anchor = td.find('a')
            if anchor:
                print(f'--- Getting {anchor["href"]}:')
                day_url = url.replace('catalog.html', anchor['href'])
                self.get_day(day_url)