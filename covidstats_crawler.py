from bs4 import BeautifulSoup
import requests
import re
# database
import pymongo


# setup connection to mongodb
conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)
# select database and collection to use
db = client.events_db
covidstats = db.covidstats

# main url
url = 'https://www.coronavirus.vic.gov.au/victorian-coronavirus-covid-19-data'

response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

# take the first section for active cases only
results = soup.find('div',class_='ch-daily-update__row')

class_args = {
    'number_cases':'ch-daily-update__statistics-item-text'
    ,'description':'ch-daily-update__statistics-item-description'
}

# function to remove the "," and convert into interger
def str_to_int(str):
    return int(str.replace(',',''))

# scrape the number of active cases, including new cases, active cases and internationally acquired cases
active_cases = {
    'new_cases' : str_to_int(results.find_all('div',class_=class_args.get('number_cases'))[0].text),
    'active_cases' : str_to_int(results.find_all('div',class_=class_args.get('number_cases'))[2].text),
    'international_cases' : str_to_int(results.find_all('div',class_=class_args.get('number_cases'))[1].text)
}

# scrape the date of the update
# extract date time update
date_time = soup.find('div',class_='rpl-markup__inner').find('h2').text
# regex to extract only the date
date_time_pattern = re.compile('Updated: (.*) (?:\d+:\d+.*)')
# search for date from matches
date_time = re.findall(date_time_pattern,date_time)[0]


# turn it to a dict
update_entry = {
    'date_time' : date_time,
    'active_cases' : active_cases
}

# insert into database if the current date's update is not existed, otherwise update
filter = {'date_time': date_time}
covidstats.replace_one(filter, update_entry, upsert=True)