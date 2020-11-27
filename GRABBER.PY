import requests
import mysql.connector
import lxml
import aiohttp
import asyncio

from extraction import ExtractionClient
from database import DBManager


db = DBManager(de_name='buy_list')
db.set_queries('bama')

client = ExtractionClient()
client.extractor('BamaExtraction')

def Page_numbers():
    response = requests.get('https://bama.ir/car/all-brands/all-models/all-trims?hasprice=true&page=')
    soup = BeautifulSoup(response.content, 'lxml')
    h = soup.find('h4').text
    cases = int(''.join([i for i in h if i in '0123456789']))
    pages = cases // 30 + 1
    return pages


async def Scraper():
    pages = Page_numbers()
    async with aiohttp.ClientSession() as session:
        for i in range(1, pages):
            async with session.get(
                'https://bama.ir/car/all-brands/all-models/all-trims?hasprice=true&page=' + str(i)) as res:
                res = await res.text()
                soup = BeautifulSoup(res, 'lxml')
                client.soup(soup)
                
                car_data = client.extract()
                db.insert_data_to_db(car_data)
                print('page {} done!'.format(i))

        print('job done!')
        db.remove_duplicate_data()
        
    await asyncio.sleep(0.1)
    await session.close()

asyncio.run(Scraper())  