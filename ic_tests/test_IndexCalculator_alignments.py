import pandas as pd

from ic_tests.helpers import _pricedata, assert_frame, assert_index, assert_series

import pandas_market_calendars as mcal
from index_calculator import IndexCalculator

import datetime as dt

nyse = mcal.get_calendar("NYSE", open_time=dt.time(9, 30), close_time=dt.time(12))
nyse.change_time("pre", dt.time(7))
nyse.change_time("post", dt.time(14,30))
ic = IndexCalculator()

schedule = nyse.schedule("2020-12-23", "2020-12-28", start="pre", end="post")

print(schedule[["pre", "market_open", "market_close", "post"]].to_string())

# to avoid confusion when reading this, the datetime literals are written in UTC, but they will
# be converted to nyse.tz in _pricedata, to always include tz conversions in the process.
# So treat `left` and `right` like they are in nyse.tz
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
                   ], to= nyse.tz, aware= True)
right = left.set_index(left.index + pd.Timedelta("30min"))

print(left)
# PRE 12 OPEN 14.30 CLOSE 17 POST 19.30

def test_convert_pre():

    ######## PRE = END

            # starts
    ### start = True, end = False
    ic.use(schedule, "2H", pre= "end", start= True, end= False)
    goal = _pricedata([ ["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 18:30:00", 0.0, 1.0, 2.0, 3.0, 4],

                        ["2020-12-24 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-24 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 16:30:00", 0.0, 1.0, 2.0, 3.0, 6],

                        ["2020-12-28 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-28 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 18:30:00", 0.0, 1.0, 2.0, 3.0, 4]], to= nyse.tz, aware= True)


    assert_frame( # left
        ic.convert(left.tz_localize(None), tz= nyse.tz), goal.tz_localize(None), ic.settings)
    assert_frame( # right
        ic.convert(right, tz= nyse.tz, closed= "right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

    ### start = "cross", end = False
    ic.use(schedule, "2H", pre= "end", start= "cross", end= False)
    goal = _pricedata([ ["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 18:30:00", 0.0, 1.0, 2.0, 3.0, 4],

                        ["2020-12-24 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-24 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 16:30:00", 0.0, 1.0, 2.0, 3.0, 6],

                        ["2020-12-28 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-28 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 18:30:00", 0.0, 1.0, 2.0, 3.0, 4]], to= nyse.tz, aware= True)
    assert_frame( # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame( # right
        ic.convert(right, tz= nyse.tz, closed= "right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

            # ends
    ### start = False, end = True
    ic.use(schedule, "2H", pre="end", start=False, end=True)
    goal = _pricedata([["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-23 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 18:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 19:30:00", 0.0, 1.0, 2.0, 3.0, 4],

                       ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-24 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 18:00:00", 0.0, 1.0, 2.0, 3.0, 6],

                       ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-28 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 18:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 19:30:00", 0.0, 1.0, 2.0, 3.0, 4]], to= nyse.tz, aware= True)
    assert_frame(  # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame(  # right
        ic.convert(right, tz=nyse.tz, closed="right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)


    ### start = False, end = "cross"
    ic.use(schedule, "2H", pre="end", start=False, end="cross")
    goal = _pricedata([["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-23 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 18:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 20:30:00", 0.0, 1.0, 2.0, 3.0, 4],

                       ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-24 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 18:30:00", 0.0, 1.0, 2.0, 3.0, 6],

                       ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-28 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 18:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 20:30:00", 0.0, 1.0, 2.0, 3.0, 4]], to= nyse.tz, aware= True)
    assert_frame(  # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame(  # right
        ic.convert(right, tz=nyse.tz, closed="right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)


    ####### PRE = START

        # starts
    ### start = True, end = False
    ic.use(schedule, "2H", pre= "start", start= True, end= False)
    goal = _pricedata([ ["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-23 12:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 18:30:00", 0.0, 1.0, 2.0, 3.0, 4],

                        ["2020-12-24 12:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-24 12:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 16:30:00", 0.0, 1.0, 2.0, 3.0, 6],

                        ["2020-12-28 12:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-28 12:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 18:30:00", 0.0, 1.0, 2.0, 3.0, 4]], to= nyse.tz, aware= True)
    assert_frame( # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame( # right
        ic.convert(right, tz= nyse.tz, closed= "right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

    ### start = "cross", end = False
    ic.use(schedule, "2H", pre= "start", start= "cross", end= False)
    goal = _pricedata([ ["2020-12-23 10:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-23 12:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 18:30:00", 0.0, 1.0, 2.0, 3.0, 4],

                        ["2020-12-24 10:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-24 12:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 16:30:00", 0.0, 1.0, 2.0, 3.0, 6],

                        ["2020-12-28 10:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                        ["2020-12-28 12:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 18:30:00", 0.0, 1.0, 2.0, 3.0, 4]], to= nyse.tz, aware= True)
    assert_frame( # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame( # right
        ic.convert(right, tz= nyse.tz, closed= "right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)


def test_convert_rth():

    ######## RTH = END
            # starts
    ### start = True, end = False
    ic.use(schedule, "2H", rth= "end", start= True, end= False)
    goal = _pricedata([ ["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 16:00:00", 0.0, 1.0, 2.0, 3.0, 4],
                        ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 19:00:00", 0.0, 1.0, 2.0, 3.0, 2],

                        ["2020-12-24 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],

                        ["2020-12-28 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 16:00:00", 0.0, 1.0, 2.0, 3.0, 4],
                        ["2020-12-28 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 19:00:00", 0.0, 1.0, 2.0, 3.0, 2]], to= nyse.tz, aware= True)
    assert_frame( # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame( # right
        ic.convert(right, tz= nyse.tz, closed= "right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

    ### start = "cross", end = False
    ic.use(schedule, "2H", rth= "end", start= "cross", end= False)
    goal = _pricedata([ ["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 16:00:00", 0.0, 1.0, 2.0, 3.0, 4],
                        ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 19:00:00", 0.0, 1.0, 2.0, 3.0, 2],

                        ["2020-12-24 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],

                        ["2020-12-28 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 16:00:00", 0.0, 1.0, 2.0, 3.0, 4],
                        ["2020-12-28 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 19:00:00", 0.0, 1.0, 2.0, 3.0, 2]], to= nyse.tz, aware= True)
    assert_frame( # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame( # right
        ic.convert(right, tz= nyse.tz, closed= "right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

        # ends
    ### start = False, end = True
    ic.use(schedule, "2H", rth= "end", start= False, end= True)
    goal = _pricedata([ ["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 4],
                        ["2020-12-23 19:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 19:30:00", 0.0, 1.0, 2.0, 3.0, 2],

                        ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 18:00:00", 0.0, 1.0, 2.0, 3.0, 8],

                        ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 17:00:00", 0.0, 1.0, 2.0, 3.0, 4],
                        ["2020-12-28 19:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 19:30:00", 0.0, 1.0, 2.0, 3.0, 2]], to= nyse.tz, aware= True)
    assert_frame( # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame( # right
        ic.convert(right, tz= nyse.tz, closed= "right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

    ### start = False, end = "cross"
    ic.use(schedule, "2H", rth= "end", start= False, end= "cross")
    goal = _pricedata([ ["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 4],
                        ["2020-12-23 19:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 21:00:00", 0.0, 1.0, 2.0, 3.0, 2],

                        ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 18:00:00", 0.0, 1.0, 2.0, 3.0, 8],

                        ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 17:00:00", 0.0, 1.0, 2.0, 3.0, 4],
                        ["2020-12-28 19:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 21:00:00", 0.0, 1.0, 2.0, 3.0, 2]], to= nyse.tz, aware= True)
    assert_frame( # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame( # right
        ic.convert(right, tz= nyse.tz, closed= "right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)



    ##### RTH = START

            # starts
    # start = True, end = False
    ic.use(schedule, "2H", rth= "start", start= True, end= False)
    goal = _pricedata([ ["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 4],
                        ["2020-12-23 13:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 15:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 19:00:00", 0.0, 1.0, 2.0, 3.0, 2],

                        ["2020-12-24 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],

                        ["2020-12-28 12:00:00", 0.0, 1.0, 2.0, 3.0, 4],
                        ["2020-12-28 13:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 15:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 19:00:00", 0.0, 1.0, 2.0, 3.0, 2]], to= nyse.tz, aware= True)
    assert_frame(  # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame(  # right
        ic.convert(right, tz=nyse.tz, closed="right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

    # start = "cross", end = False
    ic.use(schedule, "2H", rth="start", start="cross", end=False)
    goal = _pricedata([["2020-12-23 11:00:00", 0.0, 1.0, 2.0, 3.0, 4],
                       ["2020-12-23 13:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 15:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 19:00:00", 0.0, 1.0, 2.0, 3.0, 2],

                       ["2020-12-24 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],

                       ["2020-12-28 11:00:00", 0.0, 1.0, 2.0, 3.0, 4],
                       ["2020-12-28 13:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 15:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 19:00:00", 0.0, 1.0, 2.0, 3.0, 2]], to= nyse.tz, aware= True)
    assert_frame(  # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame(  # right
        ic.convert(right, tz=nyse.tz, closed="right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

            # ends
    # start = False, end = True
    ic.use(schedule, "2H", rth="start", start=False, end=True)
    goal = _pricedata([["2020-12-23 13:00:00", 0.0, 1.0, 2.0, 3.0, 4],
                       ["2020-12-23 15:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 19:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 19:30:00", 0.0, 1.0, 2.0, 3.0, 2],

                       ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 18:00:00", 0.0, 1.0, 2.0, 3.0, 8],

                       ["2020-12-28 13:00:00", 0.0, 1.0, 2.0, 3.0, 4],
                       ["2020-12-28 15:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 19:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 19:30:00", 0.0, 1.0, 2.0, 3.0, 2]], to= nyse.tz, aware= True)
    assert_frame(  # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame(  # right
        ic.convert(right, tz=nyse.tz, closed="right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

    # start = False, end = "cross"
    ic.use(schedule, "2H", rth="start", start=False, end="cross")
    goal = _pricedata([["2020-12-23 13:00:00", 0.0, 1.0, 2.0, 3.0, 4],
                       ["2020-12-23 15:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 19:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 21:00:00", 0.0, 1.0, 2.0, 3.0, 2],

                       ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 18:00:00", 0.0, 1.0, 2.0, 3.0, 8],

                       ["2020-12-28 13:00:00", 0.0, 1.0, 2.0, 3.0, 4],
                       ["2020-12-28 15:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 19:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 21:00:00", 0.0, 1.0, 2.0, 3.0, 2]], to= nyse.tz, aware= True)
    assert_frame(  # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame(  # right
        ic.convert(right, tz=nyse.tz, closed="right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

def test_convert_post():

    ######## POST = END
            # starts
    ### start = True, end = False
    ic.use(schedule, "2H", post= "end", start= True, end= False)
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
    assert_frame( # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame( # right
        ic.convert(right, tz= nyse.tz, closed= "right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

    ### start = "cross", end = False
    ic.use(schedule, "2H", post= "end", start= "cross", end= False)
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
    assert_frame( # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame( # right
        ic.convert(right, tz= nyse.tz, closed= "right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

        # ends
    ### start = False, end = True
    ic.use(schedule, "2H", post= "end", start= False, end= True)
    goal = _pricedata([ ["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 18:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 19:30:00", 0.0, 1.0, 2.0, 3.0, 6],

                        ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 18:00:00", 0.0, 1.0, 2.0, 3.0, 8],

                        ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 18:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 19:30:00", 0.0, 1.0, 2.0, 3.0, 6]], to= nyse.tz, aware= True)
    assert_frame( # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame( # right
        ic.convert(right, tz= nyse.tz, closed= "right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

    ### start = False, end = "cross"
    ic.use(schedule, "2H", post= "end", start= False, end= "cross")
    goal = _pricedata([ ["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 18:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 20:00:00", 0.0, 1.0, 2.0, 3.0, 6],

                        ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 18:00:00", 0.0, 1.0, 2.0, 3.0, 8],

                        ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 18:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 20:00:00", 0.0, 1.0, 2.0, 3.0, 6]], to= nyse.tz, aware= True)
    assert_frame( # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame( # right
        ic.convert(right, tz= nyse.tz, closed= "right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)



    ##### POST = START

            # starts
    # start = True, end = False
    ic.use(schedule, "2H", post= "start", start= True, end= False)
    goal = _pricedata([ ["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 6],
                        ["2020-12-23 13:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 15:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 17:30:00", 0.0, 1.0, 2.0, 3.0, 8],

                        ["2020-12-24 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],

                        ["2020-12-28 12:00:00", 0.0, 1.0, 2.0, 3.0, 6],
                        ["2020-12-28 13:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 15:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 17:30:00", 0.0, 1.0, 2.0, 3.0, 8]], to= nyse.tz, aware= True)
    assert_frame(  # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame(  # right
        ic.convert(right, tz=nyse.tz, closed="right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

    # start = "cross", end = False
    ic.use(schedule, "2H", post="start", start="cross", end=False)
    goal = _pricedata([ ["2020-12-23 11:30:00", 0.0, 1.0, 2.0, 3.0, 6],
                        ["2020-12-23 13:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 15:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 17:30:00", 0.0, 1.0, 2.0, 3.0, 8],

                        ["2020-12-24 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],

                        ["2020-12-28 11:30:00", 0.0, 1.0, 2.0, 3.0, 6],
                        ["2020-12-28 13:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 15:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 17:30:00", 0.0, 1.0, 2.0, 3.0, 8]], to= nyse.tz, aware= True)
    assert_frame(  # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame(  # right
        ic.convert(right, tz=nyse.tz, closed="right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

            # ends
    # start = False, end = True
    ic.use(schedule, "2H", post="start", start=False, end=True)
    goal = _pricedata([ ["2020-12-23 13:30:00", 0.0, 1.0, 2.0, 3.0, 6],
                        ["2020-12-23 15:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 17:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 19:30:00", 0.0, 1.0, 2.0, 3.0, 8],

                        ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 18:00:00", 0.0, 1.0, 2.0, 3.0, 8],

                        ["2020-12-28 13:30:00", 0.0, 1.0, 2.0, 3.0, 6],
                        ["2020-12-28 15:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 17:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 19:30:00", 0.0, 1.0, 2.0, 3.0, 8]], to= nyse.tz, aware= True)
    assert_frame(  # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame(  # right
        ic.convert(right, tz=nyse.tz, closed="right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

    # start = False, end = "cross"
    ic.use(schedule, "2H", post="start", start=False, end="cross")
    goal = _pricedata([ ["2020-12-23 13:30:00", 0.0, 1.0, 2.0, 3.0, 6],
                        ["2020-12-23 15:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 17:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-23 19:30:00", 0.0, 1.0, 2.0, 3.0, 8],

                        ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-24 18:00:00", 0.0, 1.0, 2.0, 3.0, 8],

                        ["2020-12-28 13:30:00", 0.0, 1.0, 2.0, 3.0, 6],
                        ["2020-12-28 15:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 17:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                        ["2020-12-28 19:30:00", 0.0, 1.0, 2.0, 3.0, 8]], to= nyse.tz, aware= True)
    assert_frame(  # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame(  # right
        ic.convert(right, tz=nyse.tz, closed="right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)


def test_convert_pre_rth():
    ######## PRE = END,   RTH = END

            # starts
    ### start = True, end = False
    ic.use(schedule, "2H", pre="end", rth= "end", start=True, end=False)
    goal = _pricedata([["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 16:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 19:00:00", 0.0, 1.0, 2.0, 3.0, 2],

                       ["2020-12-24 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-24 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 16:30:00", 0.0, 1.0, 2.0, 3.0, 6],

                       ["2020-12-28 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-28 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 16:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-28 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 19:00:00", 0.0, 1.0, 2.0, 3.0, 2]], to= nyse.tz, aware= True)
    assert_frame(  # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame(  # right
        ic.convert(right, tz=nyse.tz, closed="right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

    ### start = "cross", end = False
    ic.use(schedule, "2H", pre="end", rth= "end", start="cross", end=False)
    goal = _pricedata([["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 16:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 19:00:00", 0.0, 1.0, 2.0, 3.0, 2],

                       ["2020-12-24 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-24 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 16:30:00", 0.0, 1.0, 2.0, 3.0, 6],

                       ["2020-12-28 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-28 14:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 16:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-28 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 19:00:00", 0.0, 1.0, 2.0, 3.0, 2]], to= nyse.tz, aware= True)
    assert_frame(  # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame(  # right
        ic.convert(right, tz=nyse.tz, closed="right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

            # ends
    ### start = False, end = True
    ic.use(schedule, "2H", pre="end", rth= "end", start=False, end=True)
    goal = _pricedata([["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-23 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-23 19:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 19:30:00", 0.0, 1.0, 2.0, 3.0, 2],

                       ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-24 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 18:00:00", 0.0, 1.0, 2.0, 3.0, 6],

                       ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-28 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 17:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-28 19:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 19:30:00", 0.0, 1.0, 2.0, 3.0, 2]], to= nyse.tz, aware= True)
    assert_frame(  # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame(  # right
        ic.convert(right, tz=nyse.tz, closed="right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

    ### start = False, end = "cross"
    ic.use(schedule, "2H", pre="end", rth= "end", start=False, end="cross")
    goal = _pricedata([["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-23 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-23 19:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 21:00:00", 0.0, 1.0, 2.0, 3.0, 2],

                       ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-24 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 18:30:00", 0.0, 1.0, 2.0, 3.0, 6],

                       ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-28 16:30:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 17:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-28 19:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 21:00:00", 0.0, 1.0, 2.0, 3.0, 2]], to= nyse.tz, aware= True)
    assert_frame(  # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame(  # right
        ic.convert(right, tz=nyse.tz, closed="right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)


    ####### PRE = END,      RTH = START


        # starts
    ### start = True, end = False
    ic.use(schedule, "2H", pre="end", rth= "start", start=True, end=False)
    goal = _pricedata([["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-23 15:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 19:00:00", 0.0, 1.0, 2.0, 3.0, 2],

                       ["2020-12-24 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-24 14:30:00", 0.0, 1.0, 2.0, 3.0, 6],
                       ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],

                       ["2020-12-28 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-28 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-28 15:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 19:00:00", 0.0, 1.0, 2.0, 3.0, 2]], to= nyse.tz, aware= True)
    assert_frame(  # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame(  # right
        ic.convert(right, tz=nyse.tz, closed="right"), goal, ic.settings)
    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)

    ### start = "cross", end = False
    ic.use(schedule, "2H", pre="end", rth= "start", start="cross", end=False)
    goal = _pricedata([["2020-12-23 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-23 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-23 15:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-23 19:00:00", 0.0, 1.0, 2.0, 3.0, 2],

                       ["2020-12-24 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-24 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-24 14:30:00", 0.0, 1.0, 2.0, 3.0, 6],
                       ["2020-12-24 16:00:00", 0.0, 1.0, 2.0, 3.0, 8],

                       ["2020-12-28 12:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 14:00:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-28 14:30:00", 0.0, 1.0, 2.0, 3.0, 2],
                       ["2020-12-28 15:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 17:00:00", 0.0, 1.0, 2.0, 3.0, 8],
                       ["2020-12-28 19:00:00", 0.0, 1.0, 2.0, 3.0, 2]], to= nyse.tz, aware= True)
    assert_frame(  # left
        ic.convert(left, tz=nyse.tz), goal, ic.settings)
    assert_frame(  # right
        ic.convert(right, tz=nyse.tz, closed="right"), goal, ic.settings)

    assert_index(ic.timex(tz= nyse.tz), goal.index)
    assert_series(ic.times(tz= nyse.tz), goal.index)



if __name__ == '__main__':
    ####### PRE = END,      RTH = START





    for ref, obj in locals().copy().items():
        if ref.startswith("test_"):
            print("running: ", ref)
            obj()