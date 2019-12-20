import requests
from bs4 import BeautifulSoup

url = f'https://www.prostobank.ua/depozity/any/980/30/any/any/any/any/any/any/0/200000'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}
page = requests.get(url=url, headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')
rows = soup.find_all('div', class_='row')
for row in rows:
    try:
        b = row.find('div', class_='col col-name').a.text
        r = row.find('div', class_='col col-rate').p.text.replace(',', '.')
        print(b, float(r.strip()))
    except AttributeError:
        pass
