import requests
from datetime import datetime
from bs4 import BeautifulSoup
from sqlalchemy import Column, Integer, Float, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import DATE
import pymysql

pymysql.install_as_MySQLdb()
engine = create_engine('mysql+pymysql://root:your_password@localhost/scrpr_db')

# engine = create_engine('sqlite:///scrpr.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Rates(Base):
    __tablename__ = 'rates'
    id = Column(Integer, primary_key=True)
    date = Column(DATE())
    bank_name = Column(String(60))
    currency = Column(String(3))
    period = Column(String(3))
    rate = Column(Float)
    legal_type = Column(String(15))

    def __init__(self, date, bank_name, currency, period, rate, legal_type):
        self.date = date
        self.bank_name = bank_name
        self.currency = currency
        self.period = period
        self.rate = rate
        self.legal_type = legal_type

    def __repr__(self):
        return "<Rates('%s','%s', '%s', '%s', '%s', '%s')>" % (
        self.date, self.bank_name, self.currency, self.period, self.rate, self.legal_type)


Base.metadata.create_all(engine)

currencies_list = ['980', '840', '978']
periods_list = ['30', '91', '182', '274', '365']


class RatesScrpr(object):

    currencies_dict = {'980': 'UAH', '840': 'USD', '978': 'EUR'}
    periods_dict = {'30': '1M', '91': '3M', '182': '6M', '274': '9M', '365': '12M'}
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                             '(KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}

    def __init__(self, currencies, periods):
        self.currencies = currencies
        self.periods = periods

    def prostobank_params_generator(self):
        for currency in self.currencies:
            for period in self.periods:
                url = f'https://www.prostobank.ua/depozity/any/{currency}/{period}/any/any/any/any/any/any/0/200000'
                yield url, currency, period

    def prostobiz_params_generator(self):
        for currency in self.currencies:
            for period in self.periods:
                url = f'https://www.prostobiz.ua/business/deposit/any/{currency}/{period}/any/200000'
                yield url, currency, period

    def prostobank_parser(self):

        for url, currency, period in self.prostobank_params_generator():
            page = requests.get(url=url, headers=self.headers)
            soup = BeautifulSoup(page.content, 'html.parser')
            rows = soup.find_all('div', class_='row')
            for row in rows:
                try:
                    bank_name = row.find('div', class_='col col-name').a.text
                    bank_rate = row.find('div', class_='col col-rate').p.text.replace(',', '.')
                    date = datetime.now().date()
                    row_session = Rates(date=date, bank_name=bank_name, currency=self.currencies_dict[currency],
                                        period=self.periods_dict[period], rate=float(bank_rate.strip()),
                                        legal_type='individuals')
                    session = Session()
                    session.add(row_session)
                    session.commit()

                except AttributeError:
                    pass
            print('individuals -', currency, period, '- OK')

    def prostobiz_parser(self):

        for url, currency, period in self.prostobiz_params_generator():
            page = requests.get(url=url, headers=self.headers)
            soup = BeautifulSoup(page.content, 'html.parser')
            rows = soup.find_all('div', class_='row expenses')
            for row in rows:
                try:
                    bank_name = row.find('div', class_='col col-name').a.text
                    bank_rate = row.find('div', class_='col col-rate').p.text.replace(',', '.')
                    date = datetime.now().date()
                    row_session = Rates(date=date, bank_name=bank_name, currency=self.currencies_dict[currency],
                                        period=self.periods_dict[period], rate=float(bank_rate.strip()),
                                        legal_type='legal entities')
                    session = Session()
                    session.add(row_session)
                    session.commit()

                except AttributeError:
                    pass
            print('legal entities -', currency, period, '- OK')


if __name__ == '__main__':
    result = RatesScrpr(currencies=currencies_list, periods=periods_list)
    result.prostobank_parser()
    result.prostobiz_parser()
