import sys

from data_fetcher import DataFetcher


def main():
    data_fetcher = DataFetcher()
    data_fetcher.get_month('https://thredds.met.no/thredds/catalog/weamyl/Satellite/meteosat-0deg/2021/06/catalog.html')


if __name__ == '__main__':
    sys.setrecursionlimit(25000)
    main()
