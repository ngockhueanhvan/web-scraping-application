# import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from splinter import browser
import time
from webdriver_manager.chrome import ChromeDriverManager

# database
import pymongo
import re

# setup connection to mongodb
conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)

# select database and collection to use
db = client.events_db
eventbrite = db.eventbrite

# set up driver
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
driver.set_window_size(1024, 600)
driver.maximize_window()

# url to strat scraping
url = 'https://www.eventbrite.com/d/australia--melbourne/events--this-weekend/'

# class reference for each piece of info
class_args = {
    'title' : 'eds-is-hidden-accessible'
    , 'link' : 'eds-event-card-content__action-link'
    , 'date_time' : 'eds-event-card-content__sub-title eds-text-color--ui-orange eds-l-pad-bot-1 eds-l-pad-top-2 eds-text-weight--heavy eds-text-bm'
    , 'location' : 'card-text--truncated__one'
    , 'price' : 'eds-event-card-content__sub eds-text-bm eds-text-color--ui-600 eds-l-mar-top-1'
    , 'organisation_name' : 'eds-event-card__sub-content--organizer eds-text-color--ui-800 eds-text-weight--heavy card-text--truncated__two'
    , 'number_followers' : 'eds-event-card__sub-content--signal eds-text-color--ui-800 eds-text-weight--heavy'
    , 'thumbnail' : 'eds-event-card-content__image lazyload'

}   

# function to convert str to int (followers)
def followers_to_int(str):
    re_pattern = r'(.*) followers'
    try:
        str = re.findall(re_pattern, str)[0]
        
        # some time the thousand followers are shorten into "k"
        if 'k' in str:
            # remove 'k'
            str = str.replace('k','')
            thousand = str.split('.')[0]
            hundred = str.split('.')[1]
            return int(thousand)*1000+int(hundred)*100
        else:
            return int(str)
    except Exception as error:
        print(error)

# initialise the first page url
driver.get(url)

for x in range(7):
    # switch to another tab to scrape data on that page
    chwd = driver.window_handles
    driver.switch_to.window(chwd[-1])
    print(driver.current_url)
    time.sleep(4)

    # parse html page to soup
    soup  = BeautifulSoup(driver.page_source, 'html.parser')

    # extract events
    results = soup.find_all('article', class_ = 'eds-l-pad-all-4 eds-event-card-content eds-event-card-content--list eds-event-card-content--mini eds-event-card-content--square')
    
    # for each event, exctract key information
    for result in results:
        try:
            title = result.find('div', class_ = class_args.get('title')).text
            link = result.find('a', class_ = class_args.get('link'))['href']
            date_time = result.find('div', class_ = class_args.get('date_time')).text
            location = result.find('div', class_ = class_args.get('location')).text
            price = result.find_all('div', class_ = class_args.get('price'))[1].text
            organisation_name = result.find('div', class_ = class_args.get('organisation_name')).text
            number_followers = followers_to_int(result.find('div', class_ = class_args.get('number_followers')).text)
            thumbnail = result.find('img', class_ = class_args.get('thumbnail'))['data-src']

            # create a dictionary of the event
            event = {
                'title' : title
                , 'link' : link
                , 'date_time' : date_time
                , 'location' : location
                , 'price' : price
                , 'organisation_name' : organisation_name
                , 'number_followers' : number_followers
                , 'thumbnail' : thumbnail
            }

            filter = {'title': title}
            # insert to mongodb database
            # instead of using insert_one --- eventbrite.insert_one(event), we must use replace_one so that only add the new document in collection when the same event title is not existed
            eventbrite.replace_one(filter, event, upsert=True)

        except Exception as error:
            print(error)
        # click the 'Next' button on each page

        print('Data Uploaded')

    try:
        # click on next page if existed
        driver.find_element(By.XPATH, """//*[@id="root"]/div/div[2]/div/div/div/div[1]/div/main/div/div/section[1]/footer/div/div/ul/li[3]/button""").click()
        print("Clicked")
          
    except:
        print("Scraping Complete")