import requests
from bs4 import BeautifulSoup
import mysql.connector
import re
import lxml
import aiohttp
import asyncio


DB_NAME = 'buy_list'

TABLE = "CREATE TABLE bama (`model` varchar(30), `usage` int(15), `city` varchar(15), `year` int(4), `price` bigint(20))"
INSERT = "INSERT INTO bama (`model`, `usage`, `city`, `year`, `price`) VALUES(%s, %s, %s, %s, %s)"
ORDERS = ['CREATE TABLE temp LIKE bama', 'INSERT INTO temp SELECT DISTINCT * FROM bama',
        'DROP TABLE bama', 'RENAME TABLE temp TO bama']


def Page_numbers():
    response = requests.get('https://bama.ir/car/all-brands/all-models/all-trims?hasprice=true&page=')
    soup = BeautifulSoup(response.content, 'lxml')
    h = soup.find('h4').text
    cases = int(''.join([i for i in h if i in '0123456789']))
    pages = cases // 30 + 1
    return (pages)

   
def Cars(soup):
    cars = soup.find_all('h2', attrs = {'itemprop' : 'name', 'class' : 'persianOrder'})
    for i in range(0, len(cars)):
        cars[i] = re.sub(r'\s{2,}', '', cars[i].text.strip())
        cars[i] = re.split(r'،+', cars[i])
        cars[i] = cars[i][0]
    return (cars)


def Prices(soup):
    prices = soup.find_all('span', attrs = {'itemprop' : 'price'})
    for i in range(0, len(prices)): 
        if not prices[i] == 0:       
            prices[i] = int(prices[i]['content'])

    return(prices)


def Usage_Year(soup, id):
    usage_year = soup.find_all('div', attrs = {'class' : 'clearfix web-milage-div'})
    for i in range(0, len(usage_year)):
        usage_year[i] = re.sub(r'\s+', '', usage_year[i].text)
        usage_year[i] = re.findall(r'(\d+.\d+).*(\d{4}).*', re.sub(r',', '', usage_year[i]))
        if len(usage_year[i]) == 1 and len(usage_year[i][0]) == 2:
            if id == 'u':
                usage_year[i]= int(usage_year[i][0][0])
            elif id == 'y':
                usage_year[i] = int(usage_year[i][0][1])

    return(usage_year)


def City(soup):
    fields = soup.find_all('div', attrs = {'class' : 'symbole visible-xs'})
    cities = [i.p.text.strip() for i in fields]
    for i in range(0, len(cities)):
        cities[i] = re.sub(r'\s+', ' ', cities[i])
        cities[i] = re.split(r'\W+', cities[i])
        if cities[i][0] == 'نمایشگاه':
            cities[i] = cities[i][1]
        else:
            cities[i] = cities[i][0]
    return(cities)


def Data_prep(soup):
    model = Cars(soup)
    usage = Usage_Year(soup, id='u')
    city = City(soup)
    year = Usage_Year(soup, id='y')
    price = Prices(soup)
    car_data = [i for i in zip(model, usage, city, year, price) if all(i)]
    return car_data


def Database(DB_NAME):
    cnx = mysql.connector.connect(user='dana', password='32343234aaa')
    cursor = cnx.cursor()
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
        print('database created!')
    except:
        print('database not created!')
    try:
        cnx.database = DB_NAME
        cursor.execute(TABLE)
        print("table bama created!")
    except:
        print('no need to create table!')
    
    cnx.commit()
    cursor.close()
    cnx.close()


def Inserter(TABLE, INSERT, DB_NAME, car_data):
    cnx = mysql.connector.connect(
        user='dana', password='32343234aaa', database=DB_NAME)
    cursor = cnx.cursor()
    
    for i in car_data:
        cursor.execute(INSERT, i)

    cnx.commit()
    cursor.close()
    cnx.close()

def Duplicate(ORDERS):
    cnx = mysql.connector.connect(
        user='dana', password='32343234aaa', database=DB_NAME)
    cursor = cnx.cursor()

    for i in ORDERS:
        try:
            cursor.execute(i)
        except:
            pass
    
    cnx.commit()
    cursor.close()
    cnx.close()


# def Scraper():
#     Database(DB_NAME)
#     pages = Page_numbers()
#     for i in range(1, pages):
#         response = requests.get(
#             'https://bama.ir/car/all-brands/all-models/all-trims?hasprice=true&page=' + str(i))
#         soup = BeautifulSoup(response.content, 'lxml')
#         car_data = Data_prep(soup)
#         Inserter(TABLE, INSERT, DB_NAME, car_data)
#         print('page {} done!'.format(i))

#     Duplicate(ORDERS)
#     print('job done!')




async def Scraper():
    Database(DB_NAME)
    pages = Page_numbers()
    async with aiohttp.ClientSession() as session:
        for i in range(1, pages):
            async with session.get(
                'https://bama.ir/car/all-brands/all-models/all-trims?hasprice=true&page=' + str(i)) as res:
                res = await res.text()
                soup = BeautifulSoup(res, 'lxml')
                car_data = Data_prep(soup)
                Inserter(TABLE, INSERT, DB_NAME, car_data)
                print('page {} done!'.format(i))
        print('job done!')
        # Duplicate(ORDERS)
    await asyncio.sleep(0.1)
    await session.close()

asyncio.run(Scraper())  
# Scraper()