from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import re

class AbstractExtraction(ABC):

    instance = None

    def __new__(cls):
        if not cls.instance:
            cls.instance = DataExtraction()
        return cls.instance

    def __init__(self):
        self._soup = None

    @property
    def soup(self, new_soup):
        self._soup = new_soup    


    @abstractmethod
    def cars(self):
        pass

    @abstractmethod
    def price(self):
        pass

    @abstractmethod
    def usage_and_year(self, usage_type):
        pass

    @abstractmethod
    def cities(self):
        pass

    @abstractmethod
    def execution(self):
        pass



class BamaExtraction(AbstractExtraction):
    """
        for using this class you should:
            make an instance of fetch the existing one
            set the private variable soup to a new one
            then use the execution method
    """

    def cars(self):
        cars = self._soup.find_all('h2', attrs = {'itemprop' : 'name', 'class' : 'persianOrder'})
        for i in range(0, len(cars)):
            cars[i] = re.sub(r'\s{2,}', '', cars[i].text.strip())
            cars[i] = re.split(r'،+', cars[i])
            cars[i] = cars[i][0]
        return cars
    
    def price(self):
        prices = self._soup.find_all('span', attrs = {'itemprop' : 'price'})
        for i in range(0, len(prices)): 
            if not prices[i] == 0:       
                prices[i] = int(prices[i]['content'])

        return prices

    def usage_and_year(self, usage_type):
        usage_year = self._soup.find_all('div', attrs = {'class' : 'clearfix web-milage-div'})
        for i in range(0, len(usage_year)):
            usage_year[i] = re.sub(r'\s+', '', usage_year[i].text)
            usage_year[i] = re.findall(r'(\d+.\d+).*(\d{4}).*', re.sub(r',', '', usage_year[i]))
            if len(usage_year[i]) == 1 and len(usage_year[i][0]) == 2:
                if usage_type == 'u':
                    usage_year[i]= int(usage_year[i][0][0])
                elif usage_type == 'y':
                    usage_year[i] = int(usage_year[i][0][1])

        return usage_and_year

    def cities(self):
        fields = self._soup.find_all('div', attrs = {'class' : 'symbole visible-xs'})
        cities = [i.p.text.strip() for i in fields]
        for i in range(0, len(cities)):
            cities[i] = re.sub(r'\s+', ' ', cities[i])
            cities[i] = re.split(r'\W+', cities[i])
            if cities[i][0] == 'نمایشگاه':
                cities[i] = cities[i][1]
            else:
                cities[i] = cities[i][0]
        return cities

    def execution(self):
        model = self.cars()
        usage = self.usage_and_year(usage_type='u')
        city = self.cities()
        year = self.usage_and_year(usage_type='y')
        price = self.price()
        car_data = [i for i in zip(model, usage, city, year, price) if all(i)]
        return car_data
    

class ExtractionClient:

    def __init__(self):
        self._soup = None
        self._extractor = None
    
    @property
    def extractor(self, extractor_name):
        try:
            extractor = eval(extractor_name)()
        except:
            raise ValueError(f"theres no such extractor named {extractor_name}")
        self._extractor = extractor

    @property
    def soup(self, new_soup):
        self._soup = new_soup

    def extract(self):
        self.extractor.soup(self._soup)
        data = self._extractor.execution()
        return data