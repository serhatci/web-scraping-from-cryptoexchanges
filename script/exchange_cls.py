"""Provides a class for creating exchange objects

List of classes:
    Exchange
"""

class Exchange:
    """ Creates an exchange object for data scraping.
    """

    def __init__(self, exc_data):
        self.name = exc_data['name']
        self.web = exc_data['web']
        self.hpc = exc_data['homePageClick']
        self.price = exc_data['price']
        self.trade = exc_data['trade']
        self.spread = exc_data['spread']
        
        # Keeps spontaneous data collected from browsers
        self.price_data = None
        self.spread_data = None
        self.trade_data = None
        
        # Keeps spontaneous time & date of price data collected
        self.price_time = None 
        self.price_date = None
        
        # Keeps old trade history for comparison
        self.trade_data_old = [[0, 0, 0]]



 
