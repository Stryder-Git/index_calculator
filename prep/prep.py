from pandas import pd

from functools import cached_property
import exceptions as ex

class Prep:
    """
    Provides the functionality of inspecting the index, with particular regard for a
    market calendar schedule.

    This will cache a lot of functionality and only cares about the index so the init
    method should be rerun when a new dataframe doesn't have the exact same index

    --> Only generates and caches information, no changes are made here
    """

    possible_date_columns = ["index", "unnamed: 0", "date", "time", "datetime", "timestamp", "date time"]

    default_agg_map = {"open": "first", "high": "max", "low": "min",
                         "close": "last", "volume": "sum"}
    default_agg = "last"

    @classmethod
    def set_padding_options(cls, direction= "ffill", per_day= True):
        cls.PAD_DIRECTION = direction
        cls.PAD_PER_SESSION = per_day

    def __init__(self, df, market_calendar="NYSE", custom_pre= None,
                 custom_post= None, schedule= None):
        """


        :param df:
        :param market_calendar:
        :param custom_pre:
        :param custom_post:
        :param schedule:
        """
        if market_calendar is None and schedule is None:
            raise ex.InvalidConfiguration("You need to declare a market_calendar or pass a schedule")
        if not isinstance(df, pd.DataFrame):
            try: df = df.to_frame()
            except AttributeError:
                raise ex.InvalidInput("passed data needs to be a DataFrame or a Series.")

        if df.empty: raise ex.InvalidInput("passed DataFrame is empty")
        self._df = self._set_datetimeindex(df.copy())
        self._validate_timeframe()

        self._has_custom_schedule = not schedule is None
        if self._has_custom_schedule:
            self.index = self.df.index # will ensure awareness and set tz, start and end attributes
            self.schedule = schedule  # see @schedule.setter

        else:
            # set market_calendar
            if isinstance(market_calendar, str): self.market_calendar = mcal.get_calendar(market_calendar)
            else: self.market_calendar = market_calendar

            # prepare index and timezone
            if self.df.index.tz is None: self._df = self.df.tz_localize(self.market_calendar.tz)
            self.index = self.df.index

            # handle custom extended hours
            notcust = sum([custom_pre is None, custom_post is None])
            if notcust == 1: raise ValueError("both or neither of custom_pre and custom_post must be specified")
            else: self._has_custom_pre_post = notcust == 0

            if self._has_custom_pre_post:
                try: self.market_calendar.change_time("pre", custom_pre)
                except AssertionError: self.market_calendar.add_time("pre", custom_pre)
                try: self.market_calendar.change_time("post", custom_post)
                except AssertionError: self.market_calendar.add_time("post", custom_post)

            # set the schedule
            self._schedule = self.market_calendar.schedule(self.start, self.end, market_times="all", tz=self.tz)
            if self.only_rth: self._schedule = self._schedule[["market_open", "market_close"]]
            self.ic = self.IC(self.schedule, self.timeframe)

        self._custom_pre = custom_pre
        self._custom_post = custom_post
        self._data_source = None
        self._check_init()
        self.is_set = isinstance(self.columns, pd.MultiIndex)

        self._timestamp_min = pd.Timestamp.min.tz_localize(self.tz)

    # NONE
    # since it is only called on single dfs before set-construction
    @classmethod
    def _set_datetimeindex(cls, df):
        if not isinstance(df.index, pd.DatetimeIndex):
            column = df.columns[df.columns.str.lower().isin(cls.possible_date_columns)]
            if column.shape[0] != 1:
                raise ex.InvalidInput("Please set a DatetimeIndex or add ONE column that can be used as a datetimeindex,"
                                 f" with a name in: {cls.possible_date_columns}")
            else:
                df = df.set_index(pd.to_datetime(df[column[0]],
                                                 infer_datetime_format= True),
                                  drop= True)
                del df[column[0]]

        if not df.index.is_monotonic_increasing:
            return df.sort_index()
        else:
            return df


    # NONE/MINOR
    @classmethod
    def _create_agg_map(cls, df, level= 1):
        if isinstance(df.columns, pd.MultiIndex):
            s = pd.Series({t: cls.default_agg_map.get(t[level].lower(), cls.default_agg)
                           for t in df.columns})
            s.index = s.index.to_flat_index().astype("string")
            return s.to_dict()
        else:
            m = {col: cls.default_agg_map.get(col.lower(), cls.default_agg)
                 for col in df.columns}
            return m

    # NONE
    @property
    def df(self): return self._df
    # NONE
    @property
    def mc(self): return self.market_calendar
    # NONE


    def _verify_index(self, ix, ensure_awareness=True):
        if ensure_awareness and ix.tz is None:
            raise ex.TimeZoneException("When not setting a market_calendar, "
                                    "the dataframe must have a tz-aware DatetimeIndex.")
        if not ix.is_monotonic_increasing:
            raise ex.InvalidInput("The index must be sorted.")

        if self.nrows != ix.shape[0]:
            raise ex.InvalidInput("The length of the index doesn't match the shape of the df.")

    def _check_init(self):
        if self.index.duplicated().any():
            warnings.warn("There are duplicates in the index. Some functionality will not work properly, until"
                        " you make it unique. See the docs for the best way of handling duplicates.")

    def _validate_timeframe(self):
        if self.timeframe > self.MAX_TIMEFRAME:
            raise ex.InvalidTimeFrame("Currently only supporting intraday timeframe")

    @property
    def is_intra(self):
        return self.timeframe < self.DAILY

    @property
    def is_daily(self):
        return self.timeframe == self.DAILY

    @property
    def is_above_daily(self):
        return self.timeframe > self.DAILY

    @cached_property
    def timeframe(self):
        diffs = self.df.index[1:] - self.df.index[:-1]
        return diffs.to_series().mode().iloc[0]

    @cached_property
    def only_rth(self):
        """
        I need to compare the hours of
        market_open and market_close
            to
            hours of the index...

        how do I match them?

        match the open times
         based on

        :return:
        """
        if self._has_custom_pre_post: return False

        normal = self.index.normalize()
        hours = (self.index.to_series() - normal).groupby(normal)

        normal = self.schedule.market_open.dt.normalize()
        opens = (self.schedule.market_open - normal).set_axis(normal)

        if hours.min().lt(opens).any(): return False

        normal = self.schedule.market_close.dt.normalize()
        closes = (self.schedule.market_close - normal).set_axis(normal)
        return hours.max().lt(closes).all()

    @cached_property
    def duplicate_indexes(self): return self.index[self.index.duplicated()]

    @cached_property
    def duplicates_droppable(self):
        """
        will check if the full row (index and values are duplicated).
        True would mean that rows with the same index also contain the same values.
        False means that at least some rows with the same index have different values,
        which would require more user involvement.

        :return: bool
        """
        duplicates = self.index.duplicated(keep= False)
        if not duplicates.any(): return False

        df = self.df[duplicates].reset_index(drop= False)
        return df.duplicated(keep= False).all()

    @cached_property
    def missing_sessions(self):
        sessions = self._reindexed_sessions(self.columns[0])
        missing = sessions.transform("count").eq(0)

        df = self._reindexed[missing]
        sessions = self._sessions(df)
        return df[sessions.cumcount().eq(0)].index.to_series().reset_index(drop= True)

    def _sessions(self, df= None):
        """
        How to group by sessions?
            find the start (diff > tf)
            allocate session markers
            group by them

        :param df:
        :return:
        """
        df = self.df if df is None else df
        ix = df.index.to_series()
        starts = (ix - ix.shift()).le(self.timeframe)
        return df.groupby(ix.where(~starts, None).ffill())

    @property
    def sessions(self):
        return self._sessions()

    @cached_property
    def _reindexed(self):
        ix = self.ic.timex(frm= self.start, to= self.end, tz= self.tz)
        return self.df.reindex(ix)

    def _reindexed_sessions(self, col= None):
        df = self._reindexed
        if not col is None: df = df[col]
        return self._sessions(df)

    @cached_property
    def _missing(self):
        # drop all days that were missing entirely
        not_added_sessions = self._reindexed_sessions(self.columns[0]).transform("count").ne(0)
        df = self._reindexed[not_added_sessions]
        return df[df.isna().all(axis= 1)]

    @cached_property
    def incomplete_sessions(self):
        sessions = self._reindexed_sessions(self.columns[0])

        count = sessions.transform("count")
        not_missing_but_incomplete = count.lt(sessions.transform("size")) & count.ne(0)

        df = self._reindexed[not_missing_but_incomplete]
        sessions = self._sessions(df)
        return df[sessions.cumcount().eq(0)].index.to_series().reset_index(drop= True)

    @cached_property
    def missing_indexes(self):
        nas = self._missing
        return nas.index.to_series().reset_index(drop= True)

    # changes index WRAP
    @optional_wrap
    def rth(self, wrap=None):
        """
        Drop everything that is not between market_open and market_close.

        :param wrap:
        :return:
        """
        if self.only_rth: return self.df

        opn = self.schedule.market_open.set_axis(self.schedule.market_open).reindex(self.index)
        opns = self._sessions(opn).bfill()
        aboveopen = (opns.isna() | opns.eq(opns.index))

        close = self.schedule.market_close.set_axis(self.schedule.market_close).reindex(self.index)
        close = self._sessions(close).ffill()
        belowclose = (close.isna() & close.ne(close.index))

        return self.df[aboveopen & belowclose]



    # changes index WRAP
    @optional_wrap
    def drop_duplicate_indexes(self, wrap= None):
        return self.df[~self.index.duplicated()]

    @contextlib.contextmanager
    def _handle_multi_cols(self):
        orig_cols = self.columns
        agg_map = self._create_agg_map(self.df, level= 1)
        self.df.columns = agg_map.keys()
        yield orig_cols, agg_map
        self.df.columns = orig_cols

    # changes index WRAP
    @optional_wrap
    def make_timeframe(self, tf, wrap= None):
        with self._handle_multi_cols() as (columns, agg_map):
            if str(tf).lower() == "sessions":
                if self.any_nas:
                    raise ex.InvalidInput("please handle None values before using this method")

                new_tf = self.sessions.agg(agg_map).dropna(how= "any")

            else:
                tf = pd.Timedelta(tf)
                if self.timeframe >= tf:
                    raise ex.InvalidTimeFrame("target timeframe is not lower than original timeframe")

                if tf == self.DAILY:
                    if self.any_nas:
                        raise ex.InvalidInput("please handle None values before using this method")

                    new_tf = self.df.groupby(self.index.normalize()).agg(agg_map).dropna(how= "any")

                elif tf < self.DAILY:
                    new_tf = self.ic.convert(self.df, freq= tf, tz= self.tz, agg_map= agg_map, closed= "left")

                else:
                    raise ex.NotSupported("larger than daily not yet supported")

            new_tf.columns = columns

        return new_tf

    def _apply_padding(self, df):
        return df.fillna(method=self.PAD_DIRECTION).fillna(
            method="ffill" if self.PAD_DIRECTION == "bfill" else "bfill")

    # changes index WRAP
    @optional_wrap
    def pad_incomplete_sessions(self, wrap= None):
        grp = self._reindexed_sessions(self.columns[0])
        # get the full days that were alredy in the data and should be kept
        not_added_days = grp.transform("count").ne(0)
        df = self._apply_padding(self._reindexed_sessions() if self.PAD_PER_SESSION else self._reindexed) # if per_session, do operation on group
        return df[not_added_days].copy()

    # changes index WRAP
    @optional_wrap
    def pad_missing_sessions(self, wrap= None):
        grp = self._reindexed_sessions(self.columns[0])
        # to subset the missing dates
        added_days = grp.transform("count").eq(0)
        # only keep the missing dates because this function is for *missing* dates
        df = self._apply_padding(self._reindexed)[added_days] # dataframe of padded days
        return pd.concat([self.df, df]).sort_index() # added padded days to original and sort

    # changes index WRAP
    ## CHANGE .join IN FILLER
    def fill_missing_sessions(self, getter, use_name= None):
        filler = Filler(self, getter, use_name= use_name)
        filler.fill()
        return filler.join()


    def info(self, *args, **kwargs):
        print(f"{self.__class__}\n"
            f"incomplete: {self.incomplete_sessions.shape[0]}\n"
            f"missing: {self.missing_sessions.shape[0]}\n"
            f"timezone: {self.tz}\n\nwrapping:\n--------------------------")
        self.df.info(*args, **kwargs)
        print("--------------------------")
