
from pandas import concat


class Filler:
    """
    This should be a class that can be used to get certain dates of data using a getter

    a getter can be any class that has a get_data method that will return the data for the dates
    that are passed to it.

    it should be possible to pass a string or equivalent to set one of the built in getters


    how is it used?

        when calling Pricedata.fill_missing_sessions, initialize a Filler object with the dates and parameters

        call the filler,  which
            runs a loop
                getting data for each date, caching it, and then returning it as dfs in dictionaries
    """

    DEF_ATTEMPTS = 3

    def __init__(self, pricedata, getter, use_name= None):
        self.pdf = pricedata
        if use_name is None: self.symbol = self.pdf.name
        else: self.symbol = use_name
        self.getter = getter
        self.datatoconcat = {}
        self._data = {}
        self.attempts = self.DEF_ATTEMPTS

    def num_attempts(self, n): self.attempts = n

    def _try_get(self, date):
        attempt = 0
        while attempt < self.attempts:
            response = self.getter.get(self.symbol, "1m",
                                       date, date, onlyRTH=self.pdf.only_rth)
            if response: return response.data
            else: attempt += 1

        return response.data

    def fill(self):
        for orig_date in self.pdf.missing_sessions:
            date = orig_date.strftime("%Y-%m-%d")
            self._data[orig_date] = self._try_get(date)

    def as_df(self):
        return concat(self._data.values(), ignore_index= False).sort_index()

    def as_dct(self): return self._data

    def join(self):
        new = self.as_df().tz_localize(self.pdf.tz)
        new.columns = new.columns.str.lower()

        joined = concat([new, self.pdf.df], ignore_index= False)
        joined = self.pdf.wrap(joined)
        print(joined)
        if joined.duplicates_droppable:
            joined = joined.drop_duplicate_indexes()
        return joined









