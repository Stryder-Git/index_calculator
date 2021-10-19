
#### CAUTION

This project has mostly been created for my own enjoyment and can probably be broken easily. Do not blindly rely 
on these calculations since tests and documentation are still underdeveloped or non-existent. 

Particular caution when...
* using highly customized schedules
* using alignments with very low frequencies (4H - 1D)
* converting pricedata that you aren't certain to exactly match a schedule


I apologize for the lack of documentation, but the best way to familiarize yourself with the functionality and
usage of this class is by having a look at the test `test_ways_of_using` in [ic_tests\test_IndexCalculator.py](https://github.com/Stryder-Git/index_calculator/blob/master/ic_tests/test_IndexCalculator.py).
You can also check out [ic_tests\test_IndexCalculator_alignments.py](https://github.com/Stryder-Git/index_calculator/blob/master/ic_tests/test_IndexCalculator_alignments.py)
to see many examples.

#### Brief Explanation
This class aims to provide efficient calculations for generating a rich variety of possible datetime ranges, 
that respect any exchange schedule. It also allows converting high frequency pricedata to lower frequencies,
with (almost) the same flexibility and no loss of relevant information.

#### Brief Illustration


You will need a schedule dataframe 
```
from index_calculator import IndexCalculator
import pandas_market_calendars as mcal
nyse = mcal.get_calendar("NYSE")

sched = nyse.schedule("2021-10-18", "2021-10-18", market_times= "all")
sched.iloc[0]
>>> 
pre            2021-10-18 08:00:00+00:00
market_open    2021-10-18 13:30:00+00:00
market_close   2021-10-18 20:00:00+00:00
post           2021-10-19 00:00:00+00:00
Name: 2021-10-18 00:00:00, dtype: datetime64[ns, UTC]
```

Basic use
```
ic = IndexCalculator(sched, "2H")   # default is left closed
ic.timex()
>>>
DatetimeIndex(['2021-10-18 08:00:00+00:00', '2021-10-18 10:00:00+00:00',
               '2021-10-18 12:00:00+00:00', '2021-10-18 14:00:00+00:00',
               '2021-10-18 16:00:00+00:00', '2021-10-18 18:00:00+00:00',
               '2021-10-18 20:00:00+00:00', '2021-10-18 22:00:00+00:00'],
              dtype='datetime64[ns, UTC]', freq=None)
              
              
ic= IndexCalculator(sched, "2H", start= False, end= True) # this is how you set right closed
ic.timex() 
>>>
DatetimeIndex(['2021-10-18 10:00:00+00:00', '2021-10-18 12:00:00+00:00',
               '2021-10-18 14:00:00+00:00', '2021-10-18 16:00:00+00:00',
               '2021-10-18 18:00:00+00:00', '2021-10-18 20:00:00+00:00',
               '2021-10-18 22:00:00+00:00', '2021-10-19 00:00:00+00:00'],
              dtype='datetime64[ns, UTC]', freq=None)
 ```           

With custom alignments
```
ic = IndexCalculator(sched, "3H", start= True, end= "cross",   # closed on both sides and end will not be cut
                     market_open= "end", post= "start") # set borders to guarantee that a market time is in there
ic.timex()
>>> 

DatetimeIndex(['2021-10-18 08:00:00+00:00', '2021-10-18 11:00:00+00:00',
               '2021-10-18 13:30:00+00:00', '2021-10-18 15:00:00+00:00',  
               '2021-10-18 18:00:00+00:00', '2021-10-18 21:00:00+00:00',
               '2021-10-19 00:00:00+00:00'],
              dtype='datetime64[ns, UTC]', freq=None)
# NOTE:
# market_open (13:30) is in there and the remainder (13:30 - 11:00 = 2.5H) is in the *end* 
# post (00:00) is also in there but the remainder (15:00 - 13:30 = 1.5H) is at the *start*

ic.times()
>>>
0   2021-10-18 08:00:00+00:00
1   2021-10-18 11:00:00+00:00
2   2021-10-18 13:30:00+00:00
3   2021-10-18 15:00:00+00:00
4   2021-10-18 18:00:00+00:00
5   2021-10-18 21:00:00+00:00
6   2021-10-19 00:00:00+00:00
dtype: datetime64[ns, UTC]

```

