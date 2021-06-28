from alpha_vantage.timeseries import TimeSeries

API_KEY = 'NG5BUENG25LY2KUM'


class FinanceInterfaceDataRetriever:
    def __init__(self):
        self.ts = TimeSeries(API_KEY)

    def register_to_service(self):
        pass

    def fetch_last_quote(self, quote_name):
        quote, meta = self.ts.get_daily(symbol=quote_name)
        last_update_date = meta['3. Last Refreshed']
        #return last_update_date, quote[last_update_date]
        ret_quote = quote[last_update_date]
        return ret_quote['4. close']


    def fetch_multiple(self, quotes):
        pass
