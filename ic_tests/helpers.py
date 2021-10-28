import pandas as pd
import pandas_market_calendars as mcal
from pandas.testing import assert_index_equal, assert_frame_equal, assert_series_equal

pricecols = "date open high low close volume".split()
nysetz = mcal.get_calendar("NYSE").tz

def _pricedata(data, frm= "UTC", to= "UTC", aware= True, cols= None):
    cols = pricecols if cols is None else cols
    df = pd.DataFrame(data, columns= cols)
    df[cols[0]] = pd.to_datetime(df[cols[0]])
    df = df.set_index(cols[0], drop= True).tz_localize(frm).tz_convert(to)
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

left = _pricedata([["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-23 12:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-23 13:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-23 13:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-23 15:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-23 15:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-23 16:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-23 16:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-23 17:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-23 18:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-23 18:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-23 19:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-24 12:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-24 12:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-24 13:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-24 13:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-24 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-24 15:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-24 15:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-24 16:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-24 17:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-24 17:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-28 12:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-28 12:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-28 13:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-28 13:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-28 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-28 15:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-28 15:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-28 16:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-28 16:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-28 17:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-28 17:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-28 18:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-28 18:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                   ["2020-12-28 19:00:00", 0.0, 1.0, 2.0, 3.0, 2]
                   ], to=nysetz, aware=True)

