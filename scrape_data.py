import runpy
import pymongo
from splinter import Browser
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


# setup connection to mongodb
conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    # Run all scraping functions and store results in a dictionary
    data = {
        'top_eight_events': top_eight_events(),
        'top_four_news': top_four_news(),
        'covid_update' : covid_update(),
        'last_modified': dt.datetime.now()
    }
        
    # Stop webdriver and return data
    browser.quit()
    return data

def top_eight_events(filename = 'eventbrite_crawler.py'):

    # run the crawler
    runpy.run_path(path_name=filename)

    # select database and collection to use
    db = client.events_db
    eventbrite = db.eventbrite

    # return the list of top 8 followed events
    results = eventbrite.find().sort('number_followers',-1).limit(8)

    results_list  = [result for result in results]

    return results_list

def top_four_news(filename = 'theurbanlist_crawler.py'):

    # run the crawler
    runpy.run_path(path_name=filename)

    # select database and collection to use
    db = client.events_db
    theurbanlist = db.theurbanlist

    # return the most recent news
    results = theurbanlist.find().sort('_id',-1).limit(4)

    results_list  = [result for result in results]

    return results_list

def covid_update(filename = 'covidstats_crawler.py'):

    # run the crawler
    runpy.run_path(path_name=filename)

    # select database and collection to use
    db = client.events_db
    covidstats = db.covidstats

    # return the most recent news
    results = covidstats.find().sort('_id',-1).limit(1)

    results_list  = [result for result in results]

    return results_list[0]

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())

    # select database and collection to use
    db = client.events_db
    this_weekend = db.this_weekend
    # insert data to db
    this_weekend.insert_one(scrape_all())
