
from ic_tests.helpers import _pricedata, schedcols, assert_frame
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
    ic = IndexCalculator(schedule, "2H", pre="start", rth="end", end=True)
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
    ic = IndexCalculator(schedule, pre="start", rth="end", end=True)
    # Then you will have to set the frequency when calling .timex() or .times()
    assert_index_equal(ic.timex("2H"), goal2H)
    # Otherwise...
    with pytest.raises(InvalidConfiguration): ic.timex()

    # Just like before, you can then set a standard frequency to be able to reuse it
    ic.frequency = "3H"
    # by calling the instance directly, you can temporarily change all the settings ...
    ix = ic(schedule[["market_open", "market_close"]], "2H", pre="end", end= "cross")
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
    ix = ic(schedule, "2H", pre="start", rth="end", end=True)
    assert_index_equal(ix, goal2H)
    # because settings wouldn't be saved:
    with pytest.raises(InvalidConfiguration): ic.timex()
    with pytest.raises(InvalidConfiguration): ic.times()

    # settings can be set by calling .use()
    ic.use(schedule, "2H", pre="start", rth="end", end=True)
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

    schedule = nyse.schedule("2020-01-01", "2020-01-07", market_times= "all")
    with pytest.raises(InvalidInput):
        ic = IndexCalculator(schedule)


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
    ic = IndexCalculator(schedule, "2H", pre= "start", rth= "end", end= True)
    ix = ic.timex()
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 12:00:00+00:00', '2020-12-23 12:30:00+00:00',
         '2020-12-23 14:30:00+00:00', '2020-12-23 16:30:00+00:00',
         '2020-12-23 17:00:00+00:00', '2020-12-23 19:00:00+00:00',
         '2020-12-23 19:30:00+00:00', '2020-12-24 12:00:00+00:00',
         '2020-12-24 12:30:00+00:00', '2020-12-24 14:30:00+00:00',
         '2020-12-24 16:30:00+00:00', '2020-12-24 18:00:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))


    ic.use(schedule, "2H", pre= "start", rth= "end", end= False)
    ix = ic.timex()
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 12:00:00+00:00', '2020-12-23 12:30:00+00:00',
         '2020-12-23 14:30:00+00:00', '2020-12-23 16:30:00+00:00',
         '2020-12-23 17:00:00+00:00', '2020-12-23 19:00:00+00:00',
         '2020-12-24 12:00:00+00:00', '2020-12-24 12:30:00+00:00',
         '2020-12-24 14:30:00+00:00', '2020-12-24 16:30:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))

    ic.use(schedule, "2H", pre= "start", rth= "end", end="cross")
    ix = ic.timex()
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 12:00:00+00:00', '2020-12-23 12:30:00+00:00',
         '2020-12-23 14:30:00+00:00', '2020-12-23 16:30:00+00:00',
         '2020-12-23 17:00:00+00:00', '2020-12-23 19:00:00+00:00',
         '2020-12-23 21:00:00+00:00', '2020-12-24 12:00:00+00:00',
         '2020-12-24 12:30:00+00:00', '2020-12-24 14:30:00+00:00',
         '2020-12-24 16:30:00+00:00', '2020-12-24 18:30:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))

    ic.use(schedule, "2H", pre= "start", rth= "end", start= False, end= True)
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

    ic.use(schedule, "2H", pre= "start", start=False, end="cross")
    ix = ic.timex()
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 12:30:00+00:00', '2020-12-23 14:30:00+00:00',
         '2020-12-23 16:30:00+00:00', '2020-12-23 18:30:00+00:00',
         '2020-12-23 20:30:00+00:00', '2020-12-24 12:30:00+00:00',
         '2020-12-24 14:30:00+00:00', '2020-12-24 16:30:00+00:00',
         '2020-12-24 18:30:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))

    ic.use(schedule, "2H", pre="start", start=True, end="cross")
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

    ic.use(schedule, "2H", pre= "start", rth= "end", start= False, end= True)
    ix = ic.timex()
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 06:30:00+00:00', '2020-12-23 08:30:00+00:00',
         '2020-12-23 10:30:00+00:00', '2020-12-23 11:00:00+00:00',
         '2020-12-23 14:00:00+00:00', '2020-12-23 14:30:00+00:00',
         '2020-12-23 16:30:00+00:00', '2020-12-23 17:00:00+00:00',
         '2020-12-24 06:30:00+00:00', '2020-12-24 08:30:00+00:00',
         '2020-12-24 10:30:00+00:00', '2020-12-24 11:00:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))

    ic.use(schedule, "2H", pre= "start", brk= "start", rth= "end", start= False, end= True)
    ix = ic.timex()
    assert_index_equal(ix, pd.DatetimeIndex(
        ['2020-12-23 06:30:00+00:00', '2020-12-23 08:30:00+00:00',
         '2020-12-23 09:00:00+00:00', '2020-12-23 11:00:00+00:00',
         '2020-12-23 14:00:00+00:00', '2020-12-23 14:30:00+00:00',
         '2020-12-23 16:30:00+00:00', '2020-12-23 17:00:00+00:00',
         '2020-12-24 06:30:00+00:00', '2020-12-24 08:30:00+00:00',
         '2020-12-24 09:00:00+00:00', '2020-12-24 11:00:00+00:00'], dtype='datetime64[ns, UTC]', freq=None))


def test_convert_no_align():
    nyse = mcal.get_calendar("NYSE", open_time= dt.time(9, 30), close_time= dt.time(12))
    nyse.change_time("pre", dt.time(7))
    nyse.change_time("post", dt.time(14,30))
    schedule = nyse.schedule("2020-12-22", "2020-12-23", start= "pre", end= "post")
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

def test_convert_exceptions():
    # Either start or end must be set to False when using .convert()
    with pytest.raises(InvalidConfiguration) as e1: IndexCalculator(start= True, end= True).convert("")
    with pytest.raises(InvalidConfiguration) as e2: IndexCalculator(start= True, end= "cross").convert("")
    with pytest.raises(InvalidConfiguration) as e3: IndexCalculator(start= "cross", end= True).convert("")
    with pytest.raises(InvalidConfiguration) as e4: IndexCalculator(start= "cross", end= "cross").convert("")

    # But at least one must be something other than False
    with pytest.raises(InvalidConfiguration) as e5: IndexCalculator(start= False, end= False).convert("")

    for e in (e1,e2,e3,e4,e5):
        assert e.exconly() == "index_calculator.InvalidConfiguration:" \
                              " Exactly one of start and end should be False, when converting timeframes", \
                f"This is was the error string: \n{e.exconly()}"


def test_dependencies():

    assert IndexCalculator._some_date == pd.Timestamp("1970-01-01 00:00:00")



if __name__ == '__main__':

    # test_times_with_all_arguments()
    test_verify_schedule()

    exit()
    for ref, obj in locals().copy().items():
        if ref.startswith("test_"):
            print("running: ", ref)
            obj()
