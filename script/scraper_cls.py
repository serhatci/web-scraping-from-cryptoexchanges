"""Provides Scraper class.

List of classes:
    Scraper
"""
from datetime import date, datetime
from time import sleep
import re

from selenium import webdriver


class Scraper:
    """Provides methods for web scraping.
    """    
    __drivers = []
    # Change this value acc. to your needs
    max_number_of_tabs_in_a_browser_window = 4

    @classmethod
    def start_browser_windows(cls, exchanges):
        """Calculates number of browser windows and open them.

        In default, function assumes that there can be max 4 tabs in a
        browser window. If the number of exchanges is more than 4, 
        function creates new drivers to open an additional browser windows.

        Args:
            exchanges (list): list of exchange objects.
        """
        for _ in range(1, len(exchanges)+1, cls.max_number_of_tabs_in_a_browser_window):
            cls.__drivers.append(webdriver.Chrome('./script/chromedriver.exe'))
            cls.__drivers[-1].maximize_window()

    @classmethod
    def goto_exchange_websites(cls, exchanges):
        """Goes to exchange websites in new tabs.

        Args:
            exchanges (list): list of exchange objects
        """
        n = cls.max_number_of_tabs_in_a_browser_window
        grouped = [exchanges[i:i + n] for i in range(0, len(exchanges), n)]
        for driver_index, group in enumerate(grouped):
            cls.open_tabs(driver_index, group)

        for driver in cls.__drivers:
            cls.close_blank_tabs(driver)

    @classmethod
    def open_tabs(cls, driver_index, group):
        """Open tabs for exchanges in browser window

        Args:
            driver_index (int): index no of driver in __driver list
            group (list): group of exchanges that need tabs in browser window.
        """
        for tab_number, exc in enumerate(group):
            exc.driver = cls.__drivers[driver_index]
            exc.tab_number = tab_number
            exc.driver.execute_script("window.open('"+exc.web+"');")
            sleep(5)
            # tab_number+1 is used due to blank tab in browser
            cls.switch_to_tab(exc.driver, exc.tab_number+1)
            if exc.hpc['clickXpath']:
                cls.click(exc.driver, exc.hpc['clickXpath'], exc.tab_number+1)

    @staticmethod
    def switch_to_tab(driver, tab_number):
        """Switches between tabs.

        Args:
            driver (obj): browser window
            tab_number (int): index of tab to be switched. 
        """
        driver.switch_to_window(driver.window_handles[tab_number])

    @staticmethod
    def close_blank_tabs(driver):
        """Closes blank tabs.

        Args:
            driver (obj): browser window
        """
        driver.switch_to_window(driver.window_handles[0])
        driver.close()

    @classmethod
    def collect_data(cls, exchanges):
        """Collects Price & Spread & Trade history data.

        Args:
            exchanges (list): list of exchage objects
        """
        for exc in exchanges:
            cls.switch_to_tab(exc.driver, exc.tab_number)

            exc.price_data = cls.get_price(exc)
            print(exc.name, ' price ', exc.price_data)

            exc.spread_data = cls.get_spread(exc)
            print(exc.name, ' spread ', exc.spread_data)

            exc.trade_data = cls.get_trade_hist(exc)
            print(exc.name, ': Trade history was collected\n')

    @classmethod
    def get_price(cls, exc):
        """Collects price data from exchange website.

        Args:
            exc (obj): exchange 

        Returns:
            price [str]: price data
        """
        if exc.price['clickXpath']:
            cls.click(exc.driver, exc.price['clickXpath'], exc.tab_number)
        price = cls.get_element_data(exc.driver, exc.price['xpath'])
        price = re.findall('[0-9]+', price)
        exc.price_time = datetime.now().strftime("%H:%M:%S")
        exc.price_date = date.today().strftime('%d/%m/%Y')
        return round(float('.'.join(price)), 4)

    @classmethod
    def get_spread(cls, exc):
        """Collects spread info from exchange website.

        Args:
            exc (obj): exchange

        Returns:
            spread (float): numerical spread value
        """
        if exc.spread['clickXpath']:
            cls.click(exc.driver, exc.spread['clickXpath'], exc.tab_number)

        if exc.spread['calculate'] == 'Yes':
            sell = cls.get_element_data(exc.driver, exc.spread['xpathSell'])
            buy = cls.get_element_data(exc.driver, exc.spread['xpathBuy'])
            spread = abs(round(float(sell)-float(buy), 6))
        else:
            spread = cls.get_element_data(exc.driver, exc.spread['xpath'])
            spread = round(float(spread), 6)

        return spread if spread > 0 else 0

    @classmethod
    def get_trade_hist(cls, exc):
        """Collect trade history from exchange website

        Args:
            exc (obj): exchange

        Returns:
            (str): trade history  
        """        
        if exc.trade['clickXpath']:
            cls.click(exc.driver, exc.trade['clickXpath'], exc.tab_number)

        return cls.get_element_data(exc.driver, exc.trade['xpath'])

    @staticmethod
    def get_element_data(driver, data_path):
        """Collect data from given Xpath.

        Args:
            driver (obj): web browser 
            data_path (str): Xpath of relevant HTML element 

        Returns:
            data (str): data collected 
        """
        data = '0'
        for _ in range(1, 10):
            try:
                data = driver.find_elements_by_xpath(data_path)[0].text
                if len(data) > 2:
                    break
            except Exception as Er:
                print(Er)
                sleep(0.2)
        return data

    @classmethod
    def click(cls, driver, element, tab):
        """Clicks any given HTML element.

        Args:
            driver (obj): browser window
            element (str): Xpath of relevant HTML element
            tab (int): index no of tab where HTML element presents 
        """
        cls.switch_to_tab(driver, tab)
        while True:
            try:
                click_link = driver.find_elements_by_xpath(element)[0]
                click_link.click()
                break
            except Exception as Er:
                print(Er)
                sleep(1)
                True
