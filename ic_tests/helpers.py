import pandas as pd
import pandas_market_calendars as mcal
from pandas.testing import assert_index_equal, assert_frame_equal, assert_series_equal

schedcols = "pre market_open market_close post".split()
pricecols = "date open high low close volume".split()
nysetz = mcal.get_calendar("NYSE").tz

def _pricedata(data, frm= "UTC", to= "UTC", aware= True):
    df = pd.DataFrame(data, columns= pricecols)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date", drop= True).tz_localize(frm).tz_convert(to)
    if not aware: df = df.tz_localize(None)
    df.index.name = None
    return df

def _timestampseries(data, from_tz= "UTC", to_tz= None, aware= False):
    s = pd.Series(data, dtype= "datetime64[ns]"
                  ).dt.tz_localize(from_tz).dt.tz_convert(to_tz if not to_tz is None else nysetz)
    return s if aware else s.dt.tz_localize(None)

def _assert(func, new, goal, *args):
    try:
        func(new, goal)
    except AssertionError:
        print("="*10, "FAIL", "="*10)
        print(*args, sep= "\n")
        print(new)
        print(goal)
        raise

def assert_series(new, goal, *args):
    if not isinstance(goal, pd.Series):
        goal = pd.Series(goal, index= new.index)
    _assert(assert_series_equal, new, goal, *args)

def assert_index(new, goal, *args): _assert(assert_index_equal, new, goal, *args)
def assert_frame(new, goal, *args): _assert(assert_frame_equal, new, goal, *args)



