"""Main module to run script.
"""
import json
from datetime import datetime
from time import perf_counter, sleep
import os

from script.data_clean_save_cls import DataCleanAndSave
from script.exchange_cls import Exchange
from script.mysql_connection_cls import DataBase
from script.scraper_cls import Scraper


def run(exchanges, pair):
    """Starts wep scraping.

    Args:
        exchanges (list): exchange objects
        pair (str): Trade pair intended to download. 
    """
    while True:
        scrape_duration = scrape_data(exchanges)
        save_duration= save_data(exchanges, pair, scrape_duration)
        now = datetime.now()
        print(
            f'\n\nData collection duration: {scrape_duration}sec\n' \
                f'Data save duration: {save_duration}sec' \
                    f'\n{now}\n')
        sleep(1)

def save_data(exchanges, pair, duration):
    """Saves data to SQL database.

    Args:
        exchanges (list): list of exchange objects
        pair (str): downloaded cryptoasset pair
        duration (float): duration of web scraping in secs.

    Returns:
        [float]: duration of data saving
    """    
    start_save=perf_counter()
    for exc in exchanges:
        datasaver.standardize_trade_hist(exc)        
        datasaver.save_to_mysql(
            exc, database, pair, duration)
    end_save = perf_counter()
    return round(end_save-start_save,1)

def scrape_data(exchanges):
    """Starts data collection and measures the duration of data collection.

    Args:
        exchanges (list): list of exchange objects

    Returns:
        (float): Duration of data collection from browsers
    """    
    start_scraping = perf_counter()
    scraper.collect_data(exchanges)
    end_scraping = perf_counter()
    return round(end_scraping-start_scraping, 1)


if __name__ == "__main__":
    #### BELOW INFORMATION SHOULD BE SUBMITTED ###########
    pair = 'usdt_usd'
    db_name = 'tether'
    host= 'localhost'
    user=os.environ.get('MYSQL_USER')
    password=os.environ.get('MYSQL_PASS')
    ######################################################

    # Import exchange data
    with open('script/exchanges.json') as data:
        data = json.load(data)

    # Initializes all exchange objects
    exchanges = [Exchange(data[name]) for name in data]

    # Initializes a mySQL database obj
    database = DataBase(exchanges, pair, db_name, host, user, password)

    # Initialize datasaver obj for cleaning and saving data
    datasaver = DataCleanAndSave()

    # Initialize scraper obj
    scraper = Scraper()

    # Start browsers and goes to exchange websites
    scraper.start_browser_windows(exchanges)
    scraper.goto_exchange_websites(exchanges)

    # Start web scraping
    run(exchanges, pair)
