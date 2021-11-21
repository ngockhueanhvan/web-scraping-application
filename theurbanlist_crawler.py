# import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from splinter import browser
import time
from webdriver_manager.chrome import ChromeDriverManager
import re

# database
import pymongo
import datetime as dt

# setup connection to mongodb
conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)

# select database and collection to use
db = client.events_db
theurbanlist = db.theurbanlist

# set up driver
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
driver.set_window_size(1024, 600)
driver.maximize_window()

url = 'https://www.theurbanlist.com/melbourne/things-to-do/whats-on'

driver.get(url)
time.sleep(4)


soup  = BeautifulSoup(driver.page_source, 'html.parser')

results = soup.find_all('div', class_= re.compile('listing channel_a_list __got-images __big-target slick-slide.*'))


for result in results:
    try:
        thumbnail = result.find('img')['src']
        title = result.find('a',class_='listing-title').text
        link = result.find('a',class_='listing-title')['href']

        # create a dictionary of the news
        news = {
            'title' : title
            , 'link' : link
            , 'thumbnail' : thumbnail
            , 'inserted_on' : dt.datetime.now().strftime('%Y-%m-%d')
        }

        filter = {'title': title}
        # insert to mongodb database
        # instead of using insert_one --- eventbrite.insert_one(news), we must use replace_one so that only add the new document in collection when the same event title is not existed
        theurbanlist.replace_one(filter, news, upsert=True)
    except Exception as error:
        print(error)
