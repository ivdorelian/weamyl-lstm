import os.path

import requests
from bs4 import BeautifulSoup


class DataFetcher:

    DATA_FOLDER = 'data'

    def get_day(self, url):
        html = requests.get(url + 'catalog.html').content
        soup = BeautifulSoup(html, 'html.parser')
        for td in soup.find_all('td'):
            anchor = td.find('a')
            if anchor and '.nc' in anchor['href']:
                nc_filename = anchor.tt.text
                nc_file_data = requests.get(url.replace('catalog', 'fileServer') + nc_filename)
                with open(os.path.join(self.DATA_FOLDER, nc_filename), 'wb') as f:
                    f.write(nc_file_data.content)
                print('Saved:', nc_filename)
