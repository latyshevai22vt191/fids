import requests
from bs4 import BeautifulSoup
import csv



def get_product_on_page(url, dates):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'lxml')
    all_products = soup.find_all(class_='item-wrap')
    if len(all_products) == 0:
        return None, None, None
    for product in all_products:
        img = product.find('img').get('src')
        src = product.find('a').get('href')
        name = product.find('img').get('alt')
        price = product.find('span', class_='price').text.replace('\xa0', '')
        req = requests.get(src)

        # src_product = req.text
        # with open('index.html', 'w', encoding='utf-8') as file:
        #     file.write(src_product)
        # soup_product = BeautifulSoup(src_product, 'lxml')
        soup_product = BeautifulSoup(req.content, 'lxml')
        category = ''
        categories = soup_product.find('div', class_='breadcrumbs').find('ul').find_all('li')[1:-1]
        for cat in categories:
            category += cat.text.replace('\n', '').strip()
        id = soup_product.find('p', class_='sku')
        if id != None:
            id = id.text
        else:
            id = 'По умолчанию'
        is_available = soup_product.find('p', class_='availability in-stock')
        description = soup_product.find('div', class_='short-description')
        if description == None:
            description = 'По умолчанию'
        else:
            description = description.find('div', class_='std').text
        if is_available == None:
            is_available = soup_product.find('p', class_='availability out-of-stock')
            is_available = is_available.find('a')
            if is_available != None:
                is_available = is_available.text.strip()
        else:
            is_available = is_available.text
        if is_available =='Есть в наличии':
            is_available = 'Да'
        else:
            is_available = 'Нет'
        data = [category, img, src, name, price, id, is_available, description]
        dates.append(data)

    current = soup.find('p', class_='amount').text.strip().split(' ')
    count = soup.find('p', class_='amount').text.strip().split(' ')
    if len(current) == 6:
        current = current[3]
        count = count[5]
        if current != count:
            next_url = soup.find("a", class_="next").get('href')
        else:
            next_url = None
        print(next_url)
        return count, current, next_url
    else:
        return None, None, None,
