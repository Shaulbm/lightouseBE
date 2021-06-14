import finance_interface as fi
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures as futures
from pydantic import BaseModel

TIME_CYCLE = 60

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]

class Quote:
    stock_name:str
    stock_price:str

    def __init__(self, name, price):
        self.stock_name = name
        self.stock_price = price

class QrsLogic(metaclass=Singleton):
    def __init__(self):
        self.stock_list = []
        self.stocks_results_dict = {}
        self.finance_data = fi.FinanceInterfaceDataRetriever()
        self.stock_list_lock = threading.Lock()
        self.run_periodic_lock = threading.Lock()
        self.quotes_lock = threading.Lock()

        print ("init qrs_data done")
    '''
    add the quote to the registered quotes
    '''
    def register_stock(self, stock):
        if stock is not None:
            if stock not in self.stock_list:
                self.stock_list_lock.acquire()

                try:
                    self.stock_list.append(stock)
                finally:
                    self.stock_list_lock.release()

        print ("registered {0} in stocks list".format(stock))

    '''
    remove the quote from the list
    '''
    def unregister_stock(self, stock):
        if stock in self.stock_list:
            self.stock_list_lock.acquire()
            try:
                self.stock_list.remove(stock)
            finally:
                self.stock_list_lock.release()

        print ("unregistered {0} from stocks list".format(stock))

    def get_registered_stocks(self):
        self.stock_list_lock.acquire()
        try:
            stocks_list_copy = self.stock_list
        finally:
            self.stock_list_lock.release()

        return stocks_list_copy

    def get_current_stocks(self):
        
        self.quotes_lock.acquire()
        try:
            quotes_list_copy = self.stocks_results_dict.copy()
        finally:
            self.quotes_lock.release()

        stocks_list = []

        for stock_name, quote in quotes_list_copy.items():
            stocks_list.append(Quote(name=stock_name, price=quote))

        return stocks_list

    def run_periodic(self, repeat_count):
        """[summary]
            This will run the periodic checkup
        Args:
            repeat_count ([type]): [description]
        """
        self.executor = ThreadPoolExecutor(2)
        self.executor.submit(self._get_periodic_quotes, repeat_count)


    def _get_periodic_quotes(self, repeat_count):
        self.run_periodic_lock.acquire()
        self.continue_quotes = True
        self.run_periodic_lock.release()
            
        quotes_count = 0

        print ("run periodic started")

        while self.continue_quotes:
            print ("quotes main loop count {0}".format(quotes_count))
            for stock in self.get_registered_stocks():
                try:
                    last_quote = self.finance_data.fetch_last_quote(stock)

                    self.quotes_lock.acquire()
                    try:
                        self.stocks_results_dict[stock] = last_quote
                        print("iteration {0} for stock {1} value result {2} \n".format(quotes_count, stock, last_quote))
                    finally:
                        self.quotes_lock.release()

                except Exception as e:
                    print(e)
                    continue_quotes = False

                # don't overflow by the limitation of 3 checks per minute
                time.sleep(22)

            # if list is empty, be light on cpu
            time.sleep(5)

            quotes_count += 1
            if quotes_count > repeat_count:
                print ("ending periodic")
                self.run_periodic_lock.acquire()
                self.continue_quotes = False
                self.run_periodic_lock.release()

    def end_periodic_check(self):
        self.run_periodic_lock.acquire()
        self.continue_quotes = False
        self.run_periodic_lock.release()
        