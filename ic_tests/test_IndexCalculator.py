
from ic_tests.helpers import _pricedata, assert_frame
from index_calculator import IndexCalculator, InvalidConfiguration, InvalidInput

import pandas as pd
import pytest
from pandas.testing import assert_series_equal, assert_index_equal
import datetime as dt

import pandas_market_calendars as mcal


def test_create_sessions_and_parts():
    pass

def test_ways_of_using():
    nyse = mcal.get_calendar("NYSE", open_time= dt.time(9, 30), close_time= dt.time(12))
    nyse.change_time("pre", dt.time(7))
    nyse.change_time("post", dt.time(14,30))
    schedule = nyse.schedule("2020-12-23", "2020-12-24", start= "pre", end= "post")

    goal2H = pd.DatetimeIndex(
        ['2020-12-23 12:00:00+00:00', '2020-12-23 12:30:00+00:00',
         '2020-12-23 14:30:00+00:00', '2020-12-23 16:30:00+00:00',
         '2020-12-23 17:00:00+00:00', '2020-12-23 19:00:00+00:00',
         '2020-12-23 19:30:00+00:00', '2020-12-24 12:00:00+00:00',
         '2020-12-24 12:30:00+00:00', '2020-12-24 14:30:00+00:00',
         '2020-12-24 16:30:00+00:00', '2020-12-24 18:00:00+00:00'], dtype='datetime64[ns, UTC]', freq=None)

    goal3H = pd.DatetimeIndex(
        ['2020-12-23 12:00:00+00:00', '2020-12-23 14:30:00+00:00',
         '2020-12-23 17:00:00+00:00', '2020-12-23 19:30:00+00:00',
         '2020-12-24 12:00:00+00:00', '2020-12-24 14:30:00+00:00',
         '2020-12-24 17:30:00+00:00', '2020-12-24 18:00:00+00:00'], dtype='datetime64[ns, UTC]', freq=None)

    ## FULL INITIALIZATION
    # allows the settings to be reused, which would prepare the schedule ahead of time
    ic = IndexCalculator(schedule, "2H", market_open="start", market_close="end", end=True)
    assert_index_equal(ic.timex(), goal2H)

    # passing a different frequency to .timex() or .times(),
    # will still reuse most of the preparation ...
    assert_index_equal(ic.timex("3H")  , goal3H)
    # ... and reset it back to the previous configuration
    assert_index_equal(ic.timex(), goal2H)

    # If you want to change the main frequency, just do this:
    ic.frequency = "3H"
    # this will make no more than the necessary adjustments ...
    assert_index_equal(ic.timex(), goal3H)
    # ... and keep it for the next time
    assert_index_equal(ic.timex(), goal3H)

    # calling .times() will provide a series, following the exact same logic
    srs = ic.times("2H")
    assert srs.shape[0] == goal2H.shape[0]
    assert_series_equal(srs, goal2H.to_series(index= srs.index))

    # setting dates in `frm` or `to` can calculate it for only a section
    assert_index_equal(ic.timex(frm= "2020-12-24"), pd.DatetimeIndex(
        ['2020-12-24 12:00:00+00:00', '2020-12-24 14:30:00+00:00',
         '2020-12-24 17:30:00+00:00', '2020-12-24 18:00:00+00:00'], dtype = 'datetime64[ns, UTC]', freq = None))

    assert_index_equal(ic.timex(to= "2020-12-23"), pd.DatetimeIndex(
        ['2020-12-23 12:00:00+00:00', '2020-12-23 14:30:00+00:00',
         '2020-12-23 17:00:00+00:00', '2020-12-23 19:30:00+00:00'], dtype = 'datetime64[ns, UTC]', freq = None))

    assert_index_equal(ic.timex(frm= "2020-12-23", to= "2020-12-24"), goal3H)


    #### PARTIAL INIITALIZATION
    # You can also initalize it without the frequency, preparing it partially.
    ic = IndexCalculator(schedule, market_open="start", market_close="end", end=True)
    # Then you will have to set the frequency when calling .timex() or .times()
    assert_index_equal(ic.timex("2H"), goal2H)
    # Otherwise...
    with pytest.raises(InvalidConfiguration): ic.timex()

    # Just like before, you can then set a standard frequency to be able to reuse it
    ic.frequency = "3H"
    # by calling the instance directly, you can temporarily change all the settings ...
    ix = ic(schedule[["market_open", "market_close"]], "2H", end= "cross")
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 14:30:00+00:00', '2020-12-23 16:30:00+00:00',
         '2020-12-23 18:30:00+00:00', '2020-12-24 14:30:00+00:00',
         '2020-12-24 16:30:00+00:00', '2020-12-24 18:30:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))
    # ... and have them reset to what they were before, bypassing most of the preparation
    assert_index_equal(ic.timex(), goal3H)


    ## INITIALIZATION WITHOUT SETTINGS
    ic = IndexCalculator()
    # calling it directly works, but won't keep the settings and
    # will be the slowest, since it has to prepare the settings every time
    ix = ic(schedule, "2H", market_open="start", market_close="end", end=True)
    assert_index_equal(ix, goal2H)
    # because settings wouldn't be saved:
    with pytest.raises(InvalidConfiguration): ic.timex()
    with pytest.raises(InvalidConfiguration): ic.times()

    # settings can be set by calling .use()
    ic.use(schedule, "2H", market_open="start", market_close="end", end=True)
    assert_index_equal(ic.timex(), goal2H)
    # and they will be kept
    assert_index_equal(ic.timex(), goal2H)

    # same goes for .times()
    srs = ic.times()
    assert srs.shape[0] == goal2H.shape[0]
    assert_series_equal(srs, goal2H.to_series(index= srs.index))


def test_verify_schedule():
    nyse = mcal.get_calendar("NYSE", open_time= dt.time(9, 30), close_time= dt.time(12))
    nyse.change_time("pre", dt.time(10))
    nyse.change_time("post", dt.time(14, 30))

    schedule = nyse.schedule("2020-01-01", "2020-01-07", market_times= ["pre", "market_open", "market_close", "post"])
    with pytest.raises(InvalidInput):
        ic = IndexCalculator(schedule)

def test_with_odd_columns():
    cal = mcal.get_calendar("NYSE", open_time= dt.time(8), close_time=dt.time(10))
    del cal["pre"]
    del cal["post"]
    cal["first"] = dt.time(7)
    cal["second"] = dt.time(9)
    cal["third"] = dt.time(11)

    schedule = cal.schedule("2021-10-13", "2021-10-14", market_times= "all")
    schedule = schedule.rename(columns= {"market_open": "o", "market_close": "c"})
    schedule = IndexCalculator.set_schedule_tz(schedule, "Europe/Berlin")

    with pytest.raises(InvalidConfiguration):
        ic = IndexCalculator(schedule, start= False, end= True, first= "start", c= "end")

    ic = IndexCalculator(schedule, frequency= "25min", start= False, end= True,
                         c= "end", second= "start")

    assert str(ic.schedtz) == "Europe/Berlin"

    assert_index_equal(ic.timex(), pd.DatetimeIndex(
        ['2021-10-13 13:20:00+02:00', '2021-10-13 13:45:00+02:00',
         '2021-10-13 14:10:00+02:00', '2021-10-13 14:35:00+02:00',
         '2021-10-13 15:00:00+02:00', '2021-10-13 15:25:00+02:00',
         '2021-10-13 15:50:00+02:00', '2021-10-13 16:00:00+02:00',
         '2021-10-13 16:25:00+02:00', '2021-10-13 16:50:00+02:00',
         '2021-10-13 17:00:00+02:00', '2021-10-14 13:20:00+02:00',
         '2021-10-14 13:45:00+02:00', '2021-10-14 14:10:00+02:00',
         '2021-10-14 14:35:00+02:00', '2021-10-14 15:00:00+02:00',
         '2021-10-14 15:25:00+02:00', '2021-10-14 15:50:00+02:00',
         '2021-10-14 16:00:00+02:00', '2021-10-14 16:25:00+02:00',
         '2021-10-14 16:50:00+02:00', '2021-10-14 17:00:00+02:00'], dtype='datetime64[ns, Europe/Berlin]', freq=None))



def test_timezone_functionality():
    nyse = mcal.get_calendar("NYSE", open_time= dt.time(9, 30), close_time= dt.time(12))
    schedule = nyse.schedule("2020-12-22", "2020-12-23")
    ic = IndexCalculator(schedule, "2H")

    assert_series_equal(ic.times(), pd.Series(
        ['2020-12-22 14:30:00+00:00', '2020-12-22 16:30:00+00:00',
         '2020-12-23 14:30:00+00:00', '2020-12-23 16:30:00+00:00'], dtype='datetime64[ns, UTC]'))

    assert_series_equal(ic.times(frequency="3H", tz= "America/New_York"), pd.Series(
        ['2020-12-22 09:30:00-05:00', '2020-12-23 09:30:00-05:00'], dtype='datetime64[ns, America/New_York]'))

    assert_index_equal(ic.timex(tz= "Hongkong"), pd.DatetimeIndex(
        ['2020-12-22 22:30:00+08:00', '2020-12-23 00:30:00+08:00',
         '2020-12-23 22:30:00+08:00', '2020-12-24 00:30:00+08:00'], dtype='datetime64[ns, Hongkong]', freq=None))


def test_schedule_col_combinations():
    ic = IndexCalculator()

    # ONLY MARKET_OPEN AND MARKET_CLOSE
    nyse = mcal.get_calendar("NYSE", open_time= dt.time(9, 30), close_time= dt.time(12))
    schedule = nyse.schedule("2020-12-22", "2020-12-23")
    assert_index_equal(ic(schedule, "2H"), pd.DatetimeIndex(
        ['2020-12-22 14:30:00+00:00', '2020-12-22 16:30:00+00:00',
         '2020-12-23 14:30:00+00:00', '2020-12-23 16:30:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))


    # NO PRE/POST BUT WITH BREAKS
    xhkg = mcal.get_calendar("XHKG")
    schedule = xhkg.schedule("2020-12-22", "2020-12-23")
    assert_index_equal(ic(schedule, "3H"), pd.DatetimeIndex(
        ['2020-12-22 01:30:00+00:00', '2020-12-22 05:00:00+00:00',
         '2020-12-23 01:30:00+00:00', '2020-12-23 05:00:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))

    # PRE, POST, BREAKS, OPEN, CLOSE - ALL OF IT
    xhkg.add_time("pre", dt.time(8))
    xhkg.add_time("post", dt.time(18))
    schedule = xhkg.schedule("2020-12-22", "2020-12-23", start= "pre", end="post")
    assert_index_equal(ic(schedule, "3H"), pd.DatetimeIndex(
        ['2020-12-22 00:00:00+00:00', '2020-12-22 03:00:00+00:00',
         '2020-12-22 05:00:00+00:00', '2020-12-22 08:00:00+00:00',
         '2020-12-23 00:00:00+00:00', '2020-12-23 03:00:00+00:00',
         '2020-12-23 05:00:00+00:00', '2020-12-23 08:00:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))


def test_timex():
    nyse = mcal.get_calendar("NYSE", open_time= dt.time(9, 30), close_time= dt.time(12))
    nyse.change_time("pre", dt.time(7))
    nyse.change_time("post", dt.time(14, 30))

    schedule = nyse.schedule("2020-12-23", "2020-12-24", start= "pre", end= "post")

#    print(schedule[schedcols].to_string())
#
    ic = IndexCalculator(schedule, "2H", market_open= "start", market_close= "end", end= True)
    ix = ic.timex()
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 12:00:00+00:00', '2020-12-23 12:30:00+00:00',
         '2020-12-23 14:30:00+00:00', '2020-12-23 16:30:00+00:00',
         '2020-12-23 17:00:00+00:00', '2020-12-23 19:00:00+00:00',
         '2020-12-23 19:30:00+00:00', '2020-12-24 12:00:00+00:00',
         '2020-12-24 12:30:00+00:00', '2020-12-24 14:30:00+00:00',
         '2020-12-24 16:30:00+00:00', '2020-12-24 18:00:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))


    ic.use(schedule, "2H", market_open= "start", market_close= "end", end= False)
    ix = ic.timex()
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 12:00:00+00:00', '2020-12-23 12:30:00+00:00',
         '2020-12-23 14:30:00+00:00', '2020-12-23 16:30:00+00:00',
         '2020-12-23 17:00:00+00:00', '2020-12-23 19:00:00+00:00',
         '2020-12-24 12:00:00+00:00', '2020-12-24 12:30:00+00:00',
         '2020-12-24 14:30:00+00:00', '2020-12-24 16:30:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))

    ic.use(schedule, "2H", market_open= "start", market_close= "end", end="cross")
    ix = ic.timex()
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 12:00:00+00:00', '2020-12-23 12:30:00+00:00',
         '2020-12-23 14:30:00+00:00', '2020-12-23 16:30:00+00:00',
         '2020-12-23 17:00:00+00:00', '2020-12-23 19:00:00+00:00',
         '2020-12-23 21:00:00+00:00', '2020-12-24 12:00:00+00:00',
         '2020-12-24 12:30:00+00:00', '2020-12-24 14:30:00+00:00',
         '2020-12-24 16:30:00+00:00', '2020-12-24 18:30:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))

    ic.use(schedule, "2H", market_open= "start", market_close= "end", start= False, end= True)
    ix = ic.timex()
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 12:30:00+00:00', '2020-12-23 14:30:00+00:00',
         '2020-12-23 16:30:00+00:00', '2020-12-23 17:00:00+00:00',
         '2020-12-23 19:00:00+00:00', '2020-12-23 19:30:00+00:00',
         '2020-12-24 12:30:00+00:00', '2020-12-24 14:30:00+00:00',
         '2020-12-24 16:30:00+00:00', '2020-12-24 18:00:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))


    ic.use(schedule, "2H", start= True, end= "cross")
    ix = ic.timex()
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 12:00:00+00:00', '2020-12-23 14:00:00+00:00',
         '2020-12-23 16:00:00+00:00', '2020-12-23 18:00:00+00:00',
         '2020-12-23 20:00:00+00:00', '2020-12-24 12:00:00+00:00',
         '2020-12-24 14:00:00+00:00', '2020-12-24 16:00:00+00:00',
         '2020-12-24 18:00:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))

    ic.use(schedule, "2H", start=False, end="cross")
    ix = ic.timex()
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 14:00:00+00:00', '2020-12-23 16:00:00+00:00',
         '2020-12-23 18:00:00+00:00', '2020-12-23 20:00:00+00:00',
         '2020-12-24 14:00:00+00:00', '2020-12-24 16:00:00+00:00',
         '2020-12-24 18:00:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))

    ic.use(schedule, "2H", market_open= "start", start=False, end="cross")
    ix = ic.timex()
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 12:30:00+00:00', '2020-12-23 14:30:00+00:00',
         '2020-12-23 16:30:00+00:00', '2020-12-23 18:30:00+00:00',
         '2020-12-23 20:30:00+00:00', '2020-12-24 12:30:00+00:00',
         '2020-12-24 14:30:00+00:00', '2020-12-24 16:30:00+00:00',
         '2020-12-24 18:30:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))

    ic.use(schedule, "2H", market_open="start", start=True, end="cross")
    ix = ic.timex()
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 12:00:00+00:00', '2020-12-23 12:30:00+00:00',
        '2020-12-23 14:30:00+00:00', '2020-12-23 16:30:00+00:00',
        '2020-12-23 18:30:00+00:00', '2020-12-23 20:30:00+00:00',
        '2020-12-24 12:00:00+00:00', '2020-12-24 12:30:00+00:00',
        '2020-12-24 14:30:00+00:00', '2020-12-24 16:30:00+00:00',
        '2020-12-24 18:30:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))

def test_timex_w_breaks():
    ic = IndexCalculator()
    schedule = pd.DataFrame([
        ["2020-12-23 06:00:00", "2020-12-23 08:30:00", "2020-12-23 11:00:00", "2020-12-23 12:00:00", "2020-12-23 14:30:00", "2020-12-23 17:00:00"],
        ["2020-12-24 06:00:00", "2020-12-24 08:30:00", "2020-12-24 11:00:00", "2020-12-24 11:00:00", "2020-12-24 11:00:00", "2020-12-24 11:00:00"]
    ], columns= ["pre", "market_open", "break_start", "break_end", "market_close", "post"])
    for col in schedule.columns: schedule[col] = pd.to_datetime(schedule[col], utc= True)
    schedule.index = pd.DatetimeIndex(["2020-12-23", "2020-12-24"])

    ic.use(schedule, "2H", market_open= "start", market_close= "end", start= False, end= True)
    ix = ic.timex()
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 06:30:00+00:00', '2020-12-23 08:30:00+00:00',
         '2020-12-23 10:30:00+00:00', '2020-12-23 11:00:00+00:00',
         '2020-12-23 14:00:00+00:00', '2020-12-23 14:30:00+00:00',
         '2020-12-23 16:30:00+00:00', '2020-12-23 17:00:00+00:00',
         '2020-12-24 06:30:00+00:00', '2020-12-24 08:30:00+00:00',
         '2020-12-24 10:30:00+00:00', '2020-12-24 11:00:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))

    ic.use(schedule, "2H", market_open= "start", break_start= "start", market_close= "end", start= False, end= True)
    ix = ic.timex()
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 06:30:00+00:00', '2020-12-23 08:30:00+00:00',
         '2020-12-23 09:00:00+00:00', '2020-12-23 11:00:00+00:00',
         '2020-12-23 14:00:00+00:00', '2020-12-23 14:30:00+00:00',
         '2020-12-23 16:30:00+00:00', '2020-12-23 17:00:00+00:00',
         '2020-12-24 06:30:00+00:00', '2020-12-24 08:30:00+00:00',
         '2020-12-24 09:00:00+00:00', '2020-12-24 11:00:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))


def test_convert():
    nyse = mcal.get_calendar("NYSE", open_time= dt.time(9, 30), close_time= dt.time(12))
    nyse.change_time("pre", dt.time(7))
    nyse.change_time("post", dt.time(14,30))
    schedule = nyse.schedule("2020-12-22", "2021-12-23", start= "pre", end= "post")
    ic = IndexCalculator()

    data = _pricedata([ ["2020-12-22 12:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-22 12:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-22 13:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-22 13:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-22 14:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-22 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-22 15:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-22 15:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-22 16:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-22 16:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-22 17:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-22 17:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-22 18:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-22 18:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-22 19:00:00", 0.0, 1.0, 2.0, 3.0, 2],

                        ["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-23 12:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-23 13:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-23 13:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-23 15:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-23 15:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-23 16:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-23 16:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-23 17:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-23 18:00:00", 0.0, 1.0, 2.0, 3.0, 2], ["2020-12-23 18:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-23 19:00:00", 0.0, 1.0, 2.0, 3.0, 2]
                        ], to= nyse.tz, aware= True)

    ### NO ALIGN

    # EVENLY DIVIDES DAY
    ic.use(schedule, "2H", start= True, end= False)
    new = ic.convert(data, tz= nyse.tz)
    goal = _pricedata([ ["2020-12-22 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-22 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-22 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-22 18:00:00", 0.0, 1.0, 2.0, 3.0, 6],
                        ["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 18:00:00", 0.0, 1.0, 2.0, 3.0, 6]], to= nyse.tz, aware= True)

    assert_frame(new, goal, ic.settings)

    # DOES NOT EVENLY DIVIDE DAY
    ic.use(schedule, "2.5H", start= True, end= False)
    new = ic.convert(data, tz= nyse.tz)
    goal = _pricedata([ ["2020-12-22 12:00:00", 0.0, 1.0, 2.0, 3.0, 10],
                        ["2020-12-22 14:30:00", 0.0, 1.0, 2.0, 3.0, 10],
                        ["2020-12-22 17:00:00", 0.0, 1.0, 2.0, 3.0, 10],
                        ["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 10],
                        ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 10],
                        ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 10]], to= nyse.tz, aware= True)

    assert_frame(new, goal, ic.settings)


    # WITH ALIGN

    ic.use(schedule, "2H", start= False, end= "cross", market_open= "start")
    new = ic.convert(data)
    goal = _pricedata([ ["2020-12-22 12:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-22 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-22 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-22 18:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-22 20:30:00", 0.0, 1.0, 2.0, 3.0, 4],
                        ["2020-12-23 12:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 18:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 20:30:00", 0.0, 1.0, 2.0, 3.0, 4]], to= nyse.tz, aware= True)

    assert_frame(new, goal, ic.settings)

    # WITH ALIGN - closed right
    data.index = data.index + pd.Timedelta("30min")
    new = ic.convert(data, closed= "right")
    assert_frame(new, goal, ic.settings)

####################
# GENERAL USE DATA #
####################

nyse = mcal.get_calendar("NYSE", open_time=dt.time(9, 30), close_time=dt.time(12))
nyse.change_time("pre", dt.time(7))
nyse.change_time("post", dt.time(14, 30))
schedule = nyse.schedule("2020-12-23", "2020-12-28", start="pre", end="post")

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
                   ], to=nyse.tz, aware=True)


def test_convert_exceptions():
    # Either start or end must be set to False when using .convert()
    with pytest.raises(InvalidConfiguration) as e1: IndexCalculator(start= True, end= True).convert(left)
    with pytest.raises(InvalidConfiguration) as e2: IndexCalculator(start= True, end= "cross").convert(left)
    with pytest.raises(InvalidConfiguration) as e3: IndexCalculator(start= "cross", end= True).convert(left)
    with pytest.raises(InvalidConfiguration) as e4: IndexCalculator(start= "cross", end= "cross").convert(left)

    # But at least one must be something other than False
    with pytest.raises(InvalidConfiguration) as e5: IndexCalculator(start= False, end= False).convert(left)

    for e in (e1,e2,e3,e4,e5):
        assert e.exconly() == "index_calculator.InvalidConfiguration:" \
                              " Exactly one of start and end should be False, when converting timeframes", \
                f"This is was the error string: \n{e.exconly()}"


def test_pricedata_that_should_not_exist():
    """

    :return:
    """

    # PRE = 12, MO = 14.30, MC = 17, POST = 19.30
    sched = schedule[schedule.index.normalize() != "2020-12-24 00:00:00"]

    ###########################################################################
    # The pricedata (`left`) contains Dec 24th but the schedule has that day
    # removed, which can lead to inconsistent results.
    ###########################################################################

    ic = IndexCalculator(sched)

    # When no alignments chosen and frequency doesn't evenly divide the day,
    # it will have the issue that there is a day in the pricedata that is not in the schedule
    with pytest.raises(InvalidInput):
        _ = ic.convert(left, freq= "2.5H")


    # NEW:
    # New checks in _check_data_set_sched don't allow these quirks anymore


    # OLD:
        # When no alignments, but frequency evenly divides the day,
        # it will not have this issue but simply take the first available session start in the schedule
        # as the origin for a full df agg call
    with pytest.raises(InvalidInput):
        two = ic.convert(left, freq= "2H")

    goal = _pricedata([ ["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 18:00:00", 0.0, 1.0, 2.0, 3.0, 6],
                        ["2020-12-24 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 18:00:00", 0.0, 1.0, 2.0, 3.0, 6]], to= nyse.tz, aware= True)

    # assert_frame(two, goal, ic.settings)


    # when alignments are chosen, it doesn't matter if the frequency evenly divides a day, the
    # day that is not in the schedule will disappear completely, neither warnings nor errors
    ic.use(sched, market_open= "start", post= "start")
    goal = _pricedata([["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 10],
                       ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 10],
                       ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 10],
                       ["2020-12-28 12:00:00", 0.0, 1.0, 2.0, 3.0, 10],
                       ["2020-12-28 14:30:00", 0.0, 1.0, 2.0, 3.0, 10],
                       ["2020-12-28 17:00:00", 0.0, 1.0, 2.0, 3.0, 10]], to=nyse.tz, aware=True)
    with pytest.raises(InvalidInput):
        new = ic.convert(left, freq= "2.5H")

    # assert_frame(new, goal, ic.settings)

    goal = _pricedata([["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-23 12:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 4],
                       ["2020-12-23 15:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 17:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 12:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-28 12:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 14:30:00", 0.0, 1.0, 2.0, 3.0, 4],
                       ["2020-12-28 15:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 17:30:00", 0.0, 1.0, 2.0, 3.0, 8]], to=nyse.tz, aware=True)
    with pytest.raises(InvalidInput):
        new = ic.convert(left, freq= "2H")

    # assert_frame(new, goal, ic.settings)


    # unrelated test
    # freq is lower timeframe than the pricedata
    with pytest.raises(InvalidConfiguration):
        _ = ic.convert(left, freq= "12min")

##################
# NEEDS OPTIMIZING
##################
def test_last_bug():
    """
    I need to drill down on how to write a more specific test for this bug, and
    make sure that the calculations are correct.
    But it must have had something to do with the less clean way of grouping parts,
    which must have caused some kind of index mismatch.

        the branch old_version_odd_bug is in the state that should make this test fail.
    :return:
    """
    try:
        df = pd.read_csv("ic_tests\\test_data\\ABBV.csv", parse_dates= ["index"], index_col= "index")
    except FileNotFoundError:
        df = pd.read_csv(".\\test_data\\ABBV.csv", parse_dates=["index"], index_col="index")

    nyse = mcal.get_calendar("NYSE")
    schedule = nyse.schedule("2000-12-23", "2050-12-28", start="pre", end="post")

    ic = IndexCalculator(schedule, **{'frequency': pd.Timedelta('0 days 02:00:00'), 'start': True,
                               'end': False, 'market_open': 'start', 'post': 'start'})

    ic.convert(df, tz= nyse.tz)

# def test_basic_match():
#     """Neither alignments nor imperfect data"""
#
#     ic = IndexCalculator(schedule)
#
#     goal = p
#






















if __name__ == '__main__':

    # test_pricedata_that_should_not_exist()
    #
    # # test_times_with_all_arguments()
    # # test_with_odd_columns()
    # #

    # test_convert()
    # exit()

    for ref, obj in locals().copy().items():
        if ref.startswith("test_"):
            print("running: ", ref)
            obj()
