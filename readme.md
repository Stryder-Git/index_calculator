##CAUTION

I create the IndexCalculator class for a specific personal use and ended up building it into something that 
I just wanted to create. It allows a lot of flexibility when calculating DatetimeIndexes and converting standard 
pricedata but, except for my own usage, a lot is still untested.


There are two general purposes that this class fulfills while always respecting schedules:

    calculating datetime ranges in pd.Series or pd.DatetimeIndexes that follow a specific exchange calendar schedule

    converting high frequency time series data to lower frequencies, following 



    



