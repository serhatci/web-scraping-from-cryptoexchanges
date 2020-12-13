"""Provides DataCleanAndSave class.

List of classes:
    DataCleanAndSave
"""
import re
from datetime import date

import pandas as pd


class DataCleanAndSave:
    """Provides methods for data cleaning and saving.
    """

    @classmethod
    def standardize_trade_hist(cls, exc):
        """Cleans trade history data and convert all in same type.

        Args:
            exc (obj): exchange
        """
        if exc.trade_data:
            trade_hist_list = cls.remove_letters(exc.trade_data)
            trade_hist_list = list(zip(*(iter(trade_hist_list),) * 3))
            trade_hist = pd.DataFrame(trade_hist_list,
                                      columns=exc.trade['order'])
            trade_hist = trade_hist[['Amount', 'Price', 'Time']]
            trade_hist['Date'] = date.today().strftime('%d/%m/%Y')
            trade_hist['Amount'] = trade_hist['Amount'].astype(float)
            trade_hist['Price'] = trade_hist['Price'].astype(float)
            exc.trade_data = trade_hist.values.tolist()
        else:
            exc.trade_data = [0, 0, '', '']

    @staticmethod
    def remove_letters(text):
        """Removes all letters from trade history data.

        Args:
            text (str): trade history data

        Returns:
            (list) : trade history data including only numeric values
        """
        text = text.replace('\n', ' ').split(' ')

        def check(text):
            return re.search(r'([\d.]+:[\d.]+:[\d.]+)|([\d.]+)', text)
        return [check(i).group() for i in text if check(i)]

    @classmethod
    def save_to_mysql(cls, exc, database, pair, duration):
        """Saves all collected data to SQL database.

        Args:
            exc (obj): exchange
            database (obj): database
            pair (srt): trade pair
            duration (float): duration of data scraping process in secs
        """
        cls.save_price_spread(exc, duration, pair, database)
        difference = [
            tuple(x) for x in exc.trade_data if x not in exc.trade_data_old]
        if difference:
            cls.save_trade_hist(exc, database, difference)
            cls.update_old_trade_hist_data(exc, difference)
            print(f'{len(difference)} new trade data was saved in {exc.name}')
        else:
            print('Collected trade history data was same, '
                  'therefore not uploaded...')

    @staticmethod
    def update_old_trade_hist_data(exc, difference):
        """Updates old trade history attribute with new data.

        Args:
            exc (obj): exchange
            difference (list): new data different from old trade history
        """
        if len(exc.trade_data_old) > 1:
            for i in range(len(difference)-1, -1, -1):
                add = list(difference[i])
                exc.trade_data_old.insert(0, add)
                del exc.trade_data_old[-1]
        else:
            exc.trade_data_old = [list(x) for x in difference]

    @staticmethod
    def save_trade_hist(exc, database, difference):
        """Saves trade history

        Args:
            exc (obj): exchange
            database (obj): database
            difference (list): list of new data
        """
        sql = f'INSERT INTO {exc.name} ' \
            '(Amount, Price, Time, Date) VALUES (%s,%s,%s,%s)'
        database.upload_trade_hist(sql, difference)

    @staticmethod
    def save_price_spread(exc, duration, pair, database):
        """Saves price and spread.

        Args:
            exc (obj): exchange
            duration (float): duration of data collection
            pair (str): table name
            database (obj): database object
        """
        data = str((exc.name, exc.price_data, exc.spread_data,
                    exc.price_time, exc.price_date, duration))
        sql = f'INSERT INTO {pair} (Exchange,Price_USD,Spread,'  \
            f'Time,Date,Duration) VALUES {data}'
        database.upload_price_spread(sql)
