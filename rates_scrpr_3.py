import requests
from bs4 import BeautifulSoup

'''currencies_list = ['980', '840', '978']
periods_list = ['30', '91', '182', '274', '365']'''

currencies_list = ['980']
periods_list = ['30', '91']


def params_generator(currencies, periods):
    for curr in currencies:
        for per in periods:
            url = f'https://www.prostobank.ua/depozity/any/{curr}/{per}/any/any/any/any/any/any/0/200000'
            yield url, curr, per


def prostobank_parser(url, currency, period):

    currencies_dict = {'980': 'UAH', '840': 'USD', '978': 'EUR'}
    periods_dict = {'30': '1M', '91': '3M', '182': '6M', '274': '9M', '365': '12M'}
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                             '(KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}

    page = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    rows = soup.find_all('div', class_='row')
    for row in rows:
        try:
            bank_name = row.find('div', class_='col col-name').a.text
            bank_rate = row.find('div', class_='col col-rate').p.text.replace(',', '.')
            return bank_name, float(bank_rate.strip()), currencies_dict[currency], periods_dict[period]
        except AttributeError:
            pass


if __name__ == '__main__':
    for url, curr, per in params_generator(currencies=currencies_list, periods=periods_list):
        print(prostobank_parser(url=url, currency=curr, period=per))

