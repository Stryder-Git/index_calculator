from contextlib import contextmanager

import numpy as np
import pandas as pd
import datetime as dt


class IndexCalculator:
    """
    This class is capable of calculating a DatetimeIndex respecting any market schedule, retruning all valid Timestamps
     at the frequency given. The schedule values are assumed to be in UTC.

    The calculations will be made for each trading session. If the passed schedule-DataFrame doesn't have
    breaks, there is one trading session per day going from market_open to market_close. Otherwise there are two,
    the first one going from market_open to break_start and the second one from break_end to market_close.

    *Any trading session where start == end is considered a 'no-trading session' and will always be dropped*

    Trading sessions can be divided into parts:

        Without breaks:              E.g.: NYSE (pre = 4, open = 9.30,
                                                  close = 16, post = 20)
            part 1: [pre - open]        4 - 9.30    pre
            part 2: [open - close]      9.30 - 16   rth
            part 3: [close - post]      16 - 20     post
            --> end of the only trading session


        With breaks:                    E.g. XHKG   (pre = 1, open = 2, break_start = 4,
                                                        break_end = 5, close = 8,  post = 9)
                                                        Controlled by:
            part 1: [pre - open]            1 - 2       pre =
            part 2: [pre - breakstart]      2 - 4       break =        / rth
            --> end of the first trading session
            part 3: [breakend - close]      5 - 8       rth =
            part 4: [close - post]          8 - 9       post =
            --> end of the second trading session

    * how about continuous?

    PERMUTATIONS
        E.g.: pre 7, open 9.30, close 12, post 14.30  freq= "2H"

    closed = "left"/"right"/None
    if closed is None:
        if force_start is None:
            force_start = True
        if force_end is None:
            force_end = True

    elif closed == "left":
         if force_start is None:
            force_start = True
         if force_end is None:
            force_end = False

    elif closed == "right":
         if force_start is None:
            force_start = False
         if force_end is None:
            force_end = True

            <----->
    force_start = True/False/"cross"/None
    force_end = True/False/"cross"/None
        --> force_start/force_end will override the first value of pre(/rth)
         and the last value of (rth/)post
         * When passing None, these will be adjusted to fit the closed parameter:
            closed = "left" -> force_start = True, force_end = False
            closed = "right" -> force_start = False, force_end = True

    [Optional Choice]
        pre = "start"/"end"
        (break) = "start"/"end"
        rth = "start"/"end"
        post = "start"/"end"
    """
    """
        # no settings
            (7, ,7) 9, 11, 13, (14.30, ,15)

        # pre
            end
            (7, ,7) 9, 9.30, 11.30, 13.30, (14.30, ,15.30)
            start
            (7, ,5.30) 7.30, 9.30, 11.30, 13.30, (14.30, ,15.30)

        # rth
            end
            (7, ,7) 9, 11, 12, 14, (14.30, ,16)
            start
            (7, , 6) 8, 10, 12, 14, (14.30, ,16)

        post
            end
            (7, , 7), 9, 11, 13, (14.30, ,15)
            start
            (7, , 6.30), 8.30, 10.30, 12.30, (14.30, ,14.30)

        ##### COMBOS
        * pre/rth
        * pre/post
        * rth/post
        * pre/rth/post

        # pre + rth
                pre = "end", rth= "end"
            (7, ,7) 9, 9.30, 11.30, 12, 14, (14.30, ,16)
                    pre = "end", rth= "start"
            (7, ,7) 9, 9.30, 10, 12, 14, (14.30, ,16)
                    pre = "start", rth= "end"
            (7, ,5.30) 7.30, 9.30, 11.30, 12, 14, (14.30, ,16)
                    pre = "start", rth= "start"
            (7, ,5.30) 7, 7.30, 9.30, 10, 12, 14, (14.30, ,16)


        # pre + post

                pre= "end", post = "end"
            (7, ,7) 9, 9.30, 11.30, 13.30, (14.30, ,15.30)
                pre = "end", post = "start"
            (7, ,7) 9, 9.30, 10.30, 12.30, (14.30, ,14.30)
                pre = "start", post = "end"
            (7, ,5.30), 7.30, 9.30, 11.30, 13.30, (14.30, ,15.30)
                pre = "start", post = "start"
            (7, ,5.30), 7.30, 9.30, 10.30, 12.30, (14.30, ,14.30)


        # rth + post

                rth= "end", post = "end"
            (7, ,7) 9, 11, 12, 14, (14.30, ,16)
                rth = "end", post = "start"
            (7, ,7) 9, 11, 12, 12.30, (14.30, ,14.30)
                rth = "start", post = "end"
            (7, ,6), 8, 10, 12, 14, (14.30, ,16)
                rth = "start", post = "start"
            (7, ,6), 8, 10, 12, 12.30, (14.30, ,14.30)


        # pre + rth + post

                pre="end" rth= "end", post = "end"
            (7, ,7) 9, 9.30, 11.30, 12, 14, (14.30, ,16)
                pre="end" rth = "end", post = "start"
            (7, ,7) 9, 9.30, 11.30, 12, 12.30, (14.30, ,14.30)
                pre="end" rth = "start", post = "end"
            (7, ,7) 9, 9.30, 10, 12, 14, (14.30, ,16)

                pre="start", rth = "end", post = "end"
            (7, ,5.30), 7.30, 9.30, 11.30, 12, 14, (14.30, ,16)
                pre="start" rth = "end", post = "start"
            (7, ,5.30), 7.30, 9.30, 11.30, 12, 12.30, (14.30, ,14.30)
                pre="start" rth = "start", post = "end"
            (7, ,5.30), 7.30, 9.30, 10, 12, 14, (14.30, ,16)



        with breaks??

            the first trading session has the parts pre and break
            the second trading session has the parts rth and post
            --> force_start/force_end are applied to the start and end of EACH SESSION

             there will be overlap checks and limitations


        THREE USECASES:
            * calculate index
                * simple (no settings)

                * complex (use certain settings)
                        basically anything can be done


            * change timeframe of existing data
                * simple (no settings)

                * complex (use certain settings)
                    * detect tf settings
                    * use passed settings

                    certain ways of handling odd settings will need to be specified


            * convert timeframe settings

                * complex (use passed settings)


    """

    """
        CALCULATION

            for either usecase, I will need to determine the start and end of each section that I will calulate with
                if no settings:
                    start = session_start (pre/market_open)
                    end = session_end (break_start/post)

            1. calc index

                7, 14.30

                    calc n_bars, repeat
                    7
                    7 9
                    7 11
                    7 13
                    ...
                    grpby.cumcount, add tf, done



                if I want pre= "end", rth= "start", post = None



                    7, 9.30
                    9.30, 12
                    12, 14.30 
                    adjust to align
                    7, 9.30     <<<-- If "end", use real_start     ## otherwise calculate the calced_start and keep it
                    8, 12       <<<-- If "start", use calced_start
                    12, 14.30   <<<-- If not, use real_start      ## otherwise calculate the calced_end and keep it

                        (
                        if (pre = "start" and force_start= "cross"):
                            keep calced_start
                        if (post = "end" and force_end= "cross"):
                            keep calced_end
                        )

                    calc_n_bars(groupby.cumcount + 1) * tf
                    7 9
                    7 11  (replace)

                    8   10
                    8   12

                    12  14
                    12  16

                if force_start
                    = True
                    concatenate session starts, drop_duplicates
                    = False
                    drop anything smaller *or equal* to the session starts
                    = "cross"
                    concatentate calced_starts, drop_duplicates

                if force_end
                    = True
                    concatenate session ends, drop_duplicates
                    = False
                    drop anything larger *or equal* to the session ends
                    = "cross"
                    concatenate calced_ends, drop_duplicates



            2. change timeframe

                7, 14.30

                no settings
                    I would call resample.agg on the whole df
                    (unless it doesn't evenly divide, then I would do it per day)


                if I want pre= "end", rth= "start", post = None

                    7, 9.30
                    9.30, 12
                    12, 14.30

                    if (pre = "start" and force_start= "cross"):
                        the function creating the resampler will set the origin to calced_start

                    if (post = "end" and force_end= "cross"):





                pre "start", rth = None, post = "end"

                    7, 9.30    (5.30)
                    9.30, 14.30     (15.30)

                    --> I need a function to set up these borders

    """

    default_agg_map = {"open": "first", "high": "max", "low": "min",
                       "close": "last", "volume": "sum"}

    _accepted_columns = ["pre", "market_open", "break_start",
                         "break_end", "market_close", "post"]

    _tdzero = pd.Timedelta(0)
    _day = pd.Timedelta("1D")
    _some_date = pd.Timestamp(0)  # epoch
    _srt = "__srtclm__"
    SCHEDTZ = "UTC"

    @classmethod
    def _verify_schedule(cls, schedule):
        if any(schedule[col].dt.tz is None for col in schedule):
            raise TimeZoneException("Make sure all columns are tz aware")

        elif not schedule.columns.isin(cls._accepted_columns).all():
            raise InvalidColumns(f"Please ensure that all columns are in {cls._accepted_columns}"
                                 f"\n[ISSUE]-> {schedule.columns[~schedule.columns.isin(cls._accepted_columns)]}")

        elif schedule.columns.isin(["market_open", "market_close"]).sum() != 2:
            raise InvalidColumns(f"market_open and market_close must always be in a schedule")

        elif schedule.columns.isin(["pre", "post"]).sum() == 1:
            raise InvalidColumns(f"Either both or none of pre and post can be in a schedule")

        elif schedule.columns.isin(["break_start", "break_end"]).sum() == 1:
            raise InvalidColumns(f"Either both or none of break_start and break_end can be in a schedule")

        cols = sorted(schedule.columns, key=lambda x: cls._accepted_columns.index(x))
        for col1, col2 in zip(cols[1:], cols[:-1]):
            if schedule[col1].lt(schedule[col2]).any():
                raise InvalidInput("Some values seem to be messed up, please correct the schedule")

    @classmethod
    def set_schedule_tz(cls, schedule, to_tz):
        schedule = schedule.copy()
        for col in schedule:
            try:
                schedule[col] = schedule[col].dt.tz_convert(to_tz)
            except TypeError as e:
                raise TimeZoneException("All columns must be tz-aware") from e

        return schedule

    @staticmethod
    def tDelta(t):
        return pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)

    @classmethod
    def _add_column(cls, schedule, **kwarg):
        """will change the schedule in place and return it"""
        if len(kwarg) > 1: raise InvalidInput("Only parse one col at a time")
        col = list(kwarg.keys())[0]
        schedule[col] = schedule.index.tz_localize(None)  # create dates to manipulate
        _dates = schedule[col]  # keep reference to dates (*Series* with an index)

        if isinstance(kwarg[col], dt.time):
            schedule[col] += cls.tDelta(kwarg[col])

        elif isinstance(kwarg[col], dict):
            # make sure its sorted and None is the last value
            borders = list(kwarg[col].keys())
            try:
                borders.remove(None)
            except ValueError:
                raise InvalidInput("A dictionary of times always needs one entry with `None` as key.")
            borders = sorted(borders, key=lambda x: pd.Timestamp(x)) + [None]

            earliest = _dates.min()  # will be set to `d` after each iteration
            for d in borders:
                t = cls.tDelta(kwarg[col][d])
                if d is None:  # the current time
                    # earliest = d = the first date with new time, greater or equal to d
                    schedule.loc[_dates >= earliest, col] = _dates + t
                else:
                    # less than d
                    schedule.loc[(_dates >= earliest) & (_dates < d), col] = _dates + t

                earliest = d
        else:
            raise InvalidInput("values for the column need to be a dt.time object or a dictionary")

        return schedule

    def __init__(self, schedule=None, frequency=None, start=True, end=False,
                 pre=False, brk=False, rth=False, post=False):
        """
        :param schedule:
        :param frequency:
        :param start:
        :param end:
        :param pre:
        :param brk:
        :param rth:
        :param post:
        """

        _valid = (True, False, "cross")
        if not (start in _valid and end in _valid):
            raise InvalidConfiguration("start and end can only be True, False or 'cross'")

        if not all([x in ("start", "end", False) for x in [pre, brk, rth, post]]):
            raise InvalidConfiguration("pre, rth, and post can only be 'start', 'end' or False")

        self._freq = None if frequency is None else pd.Timedelta(frequency)
        self.has_breaks = False if schedule is None else ("break_start" in schedule
                                                          and "break_end" in schedule)
        self.start = start
        self.end = end

        self.pre = pre
        self.brk = brk or rth if self.has_breaks else False
        self.rth = rth
        self.post = post

        self._aligns = (self.pre, self.brk, self.rth, self.post)
        self._adj = self.start is not False or self.end != "cross" or any((x == "end" for x in self._aligns))
        self.align = any(self._aligns)

        if schedule is None:
            self.schedtz = self.SCHEDTZ
            self.schedule = pd.DataFrame(columns=["real", "start", "end", "session"])
            self.__frm = self._some_date
            self.__to = self._some_date
        else:
            self.schedtz = schedule.iloc[:, 0].dt.tz
            self._verify_schedule(schedule)
            self.schedule = self._create_sessions_and_parts(schedule)
            self.__frm = self.schedule.real.iat[0]
            self.__to = self.schedule.end.iat[-1]

        self.__times = None

    use = __init__

    @contextmanager
    def use_now(self, schedule, frequency, start=True, end=False,
                pre=False, brk=False, rth=False, post=False):
        original_settings = self.settings
        original_schedule = self.schedule.copy()  # keeping it seperate from settings to avoid recalculation
        original_tz = self.schedtz
        frm = self.__frm
        to = self.__to
        self.use(schedule=schedule, frequency=frequency, start=start,
                 end=end, pre=pre, brk=brk, rth=rth, post=post)
        yield
        self.use(schedule=None, **original_settings)  # passing None and setting it directly,
        self.schedule = original_schedule  # bypasses the calculation
        self.schedtz = original_tz
        self.__frm = frm
        self.__to = to

    @property
    def frequency(self):
        if self._freq is None: raise InvalidConfiguration("You never defined a frequency")
        return self._freq

    def _adjust_start_inplace(self, schedule):
        """adjusts start column and deletes _change column in place"""
        if self._freq is None: return

        if schedule._change.any():  # adjust the start values if any "start"'s were requested
            adj = (schedule.end - schedule.start) % self.frequency  # calc the part left to fill
            adj.loc[adj.ne(self._tdzero)] = self.frequency - adj
            schedule.loc[schedule._change, "start"] = schedule.start - adj  # extend it

        del schedule["_change"]

    @frequency.setter
    def frequency(self, frequency):
        self.__times = None
        self._freq = pd.Timedelta(frequency)
        if not "_change" in self.schedule:
            # _change is left in there if the start column has never been calculated
            # (i.e.: partially initialized without frequency)
            self.schedule["_change"] = self.schedule.start.ne(self.schedule.real)  # mark what needs to adj
        self.schedule["start"] = self.schedule.real  # replace calced_starts with real one
        self._adjust_start_inplace(self.schedule)

    @property
    def settings(self):
        return dict(frequency=self._freq, start=self.start, end=self.end,
                    pre=self.pre, brk=self.brk, rth=self.rth, post=self.post)

    def _create_sessions_and_parts(self, schedule):
        """
        schedule with
            open, close
            open, close, start, end
            open, close, pre, post
            open, close, start, end, pre, post

        will create a row for each part/session

        with three columns: start, end and _session

        start is the beginning of the part/session
        end is the end
        _session  is -1, 0, 1, or 2
            -1 indicating not a session
            O indicating start and end of a session
            1 indicating start is start of a session
            2 indicating end is end of a session

        all parts/sessions where start == end will be dropped entirely

        :param schedule:
        :return:
        """

        earliest = "pre" if "pre" in schedule else "market_open"
        latest = "post" if "post" in schedule else "market_close"

        parts = []
        for option, end_col in zip(self._aligns, ["market_open", "break_start", "market_close", "post"]):
            if option or (self.has_breaks and end_col == "break_start"):
                parts.append(schedule[[earliest, end_col]].copy())
                parts[-1]["_change"] = option == "start"
                earliest = end_col.replace("start", "end")  # in case of breaks

        if earliest != latest:
            parts.append(schedule[[earliest, latest]].copy())
            parts[-1]["_change"] = False

        for i in range(len(parts)): parts[i].columns = ["start", "end", "_change"]
        schedule = pd.concat(parts).sort_values(["start", "end"])
        schedule = schedule[schedule.start.ne(schedule.end)].reset_index(drop=True)

        schedule["real"] = schedule.start
        self._adjust_start_inplace(schedule)
        # create the session column to be able to seperate sessions from parts
        sessionstart = schedule.real.gt(schedule.end.shift())
        schedule.loc[sessionstart | (schedule.index == 0), "session"] = schedule.real
        schedule["session"] = schedule.session.ffill()
        return schedule

    @contextmanager
    def _temp(self, frequency):
        """temporarily reset the configured frequency"""
        if frequency is None:
            yield; return

        original_freq = self._freq
        original_start = self.schedule.start
        original_times = self.__times
        self.__times = None
        self.frequency = frequency  # will adjust starts
        yield
        self.schedule["start"] = original_start  # reset to prior
        self._freq = original_freq
        self.__times = original_times

    def _handle_start_end(self, ts):
        """This will adjust the calculated time_series (column: 'target' in ts) according to the
        start and end configuration. This can be True, False or "cross" for each of them and refers to the
        start and end of *sessions* and *not* parts. Ends of parts can never "cross" due to their continuous nature,
        and will always be curtailed to correctly align the start of the next part.
        """

        sessions = ts.groupby("session")
        # replace all part ends with their real end, except the last one, which would be a session end
        ts.loc[ts.target.gt(ts.end) & sessions.cumcount(False).ne(0), "target"] = ts.end

        # handles session ends
        if self.end != "cross":
            # set column end to be the end of the session
            ts["end"] = sessions["end"].transform("max")
            if self.end:  # replace the ones greater than session-end with session-end
                time_series = ts.target.where(ts.target.le(ts.end), ts.end)
            else:
                time_series = ts.loc[ts.target.lt(ts.end), "target"]
        else:
            time_series = ts.target

        # handles session starts
        if self.start is True:  # add the session-starts (duplicates are dropped at return)
            time_series = pd.concat([time_series, ts.session])  # add real session starts
        elif self.start == "cross":
            time_series = pd.concat([time_series, sessions["start"].min()])  # add calced session starts

        time_series.name = None
        return time_series.drop_duplicates().reset_index(drop=True)

    def _times(self, frm, to):
        """Method used by date_range to calculate the trading index.
         :return: pd.Series of datetime64[ns, UTC]"""

        if self.__times is None:
            ts = np.ceil((self.schedule.end - self.schedule.start) / self.frequency)
            ts = self.schedule.index.repeat(ts)
            ts = self.schedule.reindex(ts).reset_index(drop=True)

            ts["target"] = (ts.start.groupby(ts.real).cumcount() + 1) * self.frequency + ts.start
            if self._adj:
                self.__times = self._handle_start_end(ts).sort_values().reset_index(drop=True)
            else:
                ts.target.name = None
                self.__times = ts.target.reset_index(drop=True)

        return self.__times[self.__times.ge(frm.normalize()) &
                            self.__times.le(to.normalize() + self._day)]

    def clear(self): self.__times = None

    def times(self, frequency=None, frm=None, to=None, tz=None):
        """

        :param frequency:
        :param frm:
        :param to:
        :param tz: timezone that the resulting series should be in
        :return:
        """
        if tz is None:
            if frm is None:
                frm = self.__frm
            else:
                frm = pd.Timestamp(frm)
                try: frm = frm.tz_localize(self.schedtz)
                except TypeError: pass

            if to is None:
                to = self.__to
            else:
                to = pd.Timestamp(to)
                try: to = to.tz_localize(self.schedtz)
                except TypeError: pass

            with self._temp(frequency):
                return self._times(frm, to)

        else:
            if frm is None:
                frm = self.__frm
            else:
                frm = pd.Timestamp(frm)
                try: frm = frm.tz_localize(tz).tz_convert(self.schedtz)
                except TypeError: frm = frm.tz_convert(self.schedtz)

            if to is None:
                to = self.__to
            else:
                to = pd.Timestamp(to)
                try: to = to.tz_localize(tz).tz_convert(self.schedtz)
                except TypeError: to = to.tz_convert(self.schedtz)

            with self._temp(frequency):
                return self._times(frm, to).dt.tz_convert(tz)


    def timex(self, frequency=None, frm=None, to=None, tz=None):
        return pd.DatetimeIndex(self.times(frequency=frequency, frm=frm, to=to, tz=tz))

    def __call__(self, schedule, frequency, start=True, end=False,
                 pre=False, brk=False, rth=False, post=False):
        with self.use_now(schedule, frequency, start=start, end=end,
                          pre=pre, brk=brk, rth=rth, post=post):
            return pd.DatetimeIndex(self._times(self.__frm, self.__to))

    __call__.__doc__ = __init__.__doc__

    def _check_data_set_sched(self, data, closed):
        if data.isna().any().any():
            raise InvalidInput("Please handle the missing values in the data before using this method")

        self.__inferred_timeframe = (data.index - data.index.to_series().shift()).mode().iat[0]
        if closed != "left": data.index = data.index - self.__inferred_timeframe

        dmin, dmax = data.index[[0, -1]]
        dmax += self.__inferred_timeframe
        if dmin < self.__frm or dmax > self.__to: raise InvalidInput("Schedule doesn't cover the whole data")

        # _sched is needed by the helper functions
        self._sched = self.schedule[self.schedule.real.ge(dmin) & self.schedule.end.le(dmax)]
        if not self._sched.real.isin(data.index).all():
            raise InvalidInput("You seem to have missing data. This is not refering to NaN values but to "
                               "market times that aren't represented in your data. This may also be because your "
                               "timeframe is too large.")
        return data

    def _gen_parts_origin(self, data):
        """
        This generator will group the requested parts/sessions in `sched` by
        their start and end times and use those to yield the required subsections of `data`.

        In order to handle varying close/open times, which can lead to duplicate sections
        when only looking at the time, there is a process including date comparison and dropping
        of subsets from `data` to avoid duplicates.

        roughly, the logic is this:

            for each [unique combination of] start, end:
                select everything between start and end
                (may lead to wrong ones)
                keep only those that have dates in either real or end
                yield that
                then drop whatever was yielded from `data`
        """

        grps = self._sched.groupby(
            [self._sched.real - self._sched.real.dt.normalize(),
             self._sched.end - self._sched.end.dt.normalize()]).groups

        for (real, end), index in grps.items():
            start_dates = self._sched.loc[index, "real"].dt.normalize()  # real start_dates
            end_dates = self._sched.loc[index, "end"].dt.normalize()  # real end_dates

            # get the part based on the real start
            part = data.between_time((self._some_date + real).time(),
                                     (self._some_date + end).time(),
                                     include_start=True, include_end=False)

            ix = part.index.normalize()  # dates in the part
            part = part[ix.isin(start_dates) | ix.isin(end_dates)]  # drop any dates that don't match

            if not part.empty:  # use the calced start as origin
                start = self._sched.at[index[0], "start"]
                yield part, part.index[0].normalize() + (start - start.normalize())

    def _resample(self, firstrows, agg_map, label):
        """
        This will prepare a function that can be applied to each trading day,
        when an uneven tf has been requested.

        It will prepare the origin of each day, when creating the function, thereby
        eliminating the need to recalculate it at every iteration

        :param agg_map:
        :return:
        """
        origins = self._sched.loc[self._sched.real.isin(firstrows)]
        origins = origins["start"].set_axis(origins["real"])
        f = self.frequency

        def __new(df):
            return df.resample(f, origin=origins.at[df.index[0]], label=label
                               ).agg(agg_map)

        return __new

    def _group_first(self, data):
        ix = data.index.to_series()
        starts = (ix - ix.shift()).le(self.__inferred_timeframe)
        grp = data.groupby(ix.where(~starts, None).ffill())
        return grp, data.index[grp.cumcount().eq(0)]

    def _convert(self, data, agg_map, closed):
        """
        :param data:
        :param tz:
        :param agg_map:
        :param closed:
        :return:
        """
        label = "left" if self.start else "right"
        data = self._check_data_set_sched(data, closed)
        even = (self._day % self.frequency) == self._tdzero  # evenly divides day

        if self.align:
            assert not self._srt in data, f"Please rename column: {self._srt}."
            data[self._srt] = np.arange(data.shape[0]) # a column with integers showing the original order of the parts
            agg_map[self._srt] = "first"
            parts = []
            if even:
                for part, origin in self._gen_parts_origin(data):
                    parts.append(
                        part.resample(self.frequency, origin=origin, label=label
                                      ).agg(agg_map
                                            ).dropna(how="any"))
            else:
                for part, origin in self._gen_parts_origin(data):
                    group, first = self._group_first(part)
                    parts.append(
                        group.apply(self._resample(first, agg_map, label)
                                    ).dropna(how="any"))

            new = pd.concat(parts).sort_values(self._srt)
            new = new.set_index(pd.DatetimeIndex(self._times(self.__frm, self.__to)), drop=True
                                ).drop(columns=self._srt)
        elif even:
            new = data.resample(self.frequency, label=label, origin=self._sched.start.iat[0]
                                ).agg(agg_map).dropna(how="any")
        else:
            group, first = self._group_first(data)
            new = group.apply(self._resample(first, agg_map, label)
                              ).droplevel(0).dropna(how="any")

        new.index.freq = None
        return new

    def convert(self, data, freq=None, agg_map=None, closed="left", tz=None):
        """

        :param data: dataframe with datetimeindex to convert
        :param freq: frequency/timeframe to use instead of self.frequency
        :param agg_map: dictionary to replace self.default_agg_map if desired
        :param closed: on which side the passed `data` is closed
            (not the returned dataframe, that is determined by the start/end configuration of
             the IndexCalculator instance)
        :param tz: if the datetimeindex is timezone naive this is the timezone it should be interpreted in,
            will be ignored if the index is timezone aware
        :return: DataFrame with index in `freq` and data converted according to `agg_map`
        """


        if sum((self.start is False, self.end is False)) != 1:
            raise InvalidConfiguration("Exactly one of start and end should be False, when converting timeframes")

        try:
            _tz = data.index.tz
            data = data.tz_convert(self.schedtz)
        except TypeError as e:
            if tz is None:
                raise TimeZoneException("When the index is tz-naive, you must pass"
                                        " the tz that it should be interpreted in") from e
            is_aware = False
            data = data.tz_localize(tz).tz_convert(self.schedtz)
        else:
            is_aware = True
            tz = _tz

        if not data.index.is_monotonic_increasing: data = data.sort_index()

        if agg_map is None:
            agg_map = self.default_agg_map
            data.columns = data.columns.str.lower()

        with self._temp(freq):
            new = self._convert(data, agg_map, closed).tz_convert(tz)

        if is_aware: return new
        return new.tz_localize(None)


class IndexCalculatorException(ValueError):
    pass


class TimeZoneException(IndexCalculatorException):
    pass


class InvalidColumns(IndexCalculatorException):
    pass


class InvalidInput(IndexCalculatorException):
    pass


class InvalidConfiguration(IndexCalculatorException):
    pass


if __name__ == '__main__':
    pass
    # nyse = mcal.get_calendar("NYSE")
    # sched = nyse.schedule("2021-08-19", "2021-08-20")
    #
    #
    # ic = IndexCalculator()
    # ic.use(sched, pre= dt.time(8), post= dt.time(23))
    # print(ic.align)
    # ic.set(pre= "start", rth= "start")
    #
    #
    #