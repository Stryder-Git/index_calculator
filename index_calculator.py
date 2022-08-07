from contextlib import contextmanager

import numpy as np
import pandas as pd
import datetime as dt

__version__ = 0.2

class IndexCalculator:
    """
    An IndexCalculator is capable of calculating datetime ranges respecting exchange schedules.

    Important notes:
    * the columns of the schedule need to be sorted such that col_n <= col_n+1
    * left/right closed are set using the `start` and `end` keywards
    * any column (except the first or "break_end", which are session starts) can be aligned on, which
        is done by passing the column name as a kwarg to __init__
    * when passing a column name to __init__ the argument value must be "start" or "end", indicating where
        the remainder will be put if its not an even divide

    * pricedata conversions can follow the same configurations except that either start or end must be False

    For more illustrations, please check out the tests



    """

    default_agg_map = {"open": "first", "high": "max", "low": "min",
                       "close": "last", "volume": "sum"}

    _valid_start_end = (True, False, "cross")
    _tdzero = pd.Timedelta(0)
    _day = pd.Timedelta("1D")
    _some_date = pd.Timestamp(0)  # epoch
    _srt = "__srtclm__"
    SCHEDTZ = "UTC"

    @classmethod
    def _verify_schedule(cls, schedule):
        if any(schedule[col].dt.tz is None for col in schedule):
            raise TimeZoneException("Make sure all columns are tz aware,"
                                    " IndexCalculator.set_schedule_tz(schedule, to_tz, from_tz)"
                                    " makes this really easy")

        elif schedule.columns.isin(["break_start", "break_end"]).sum() == 1:
            raise InvalidColumns(f"Either both or none of break_start and break_end can be in a schedule")

        for col1, col2 in zip(schedule.columns[1:], schedule.columns[:-1]):
            if schedule[col1].lt(schedule[col2]).any():
                raise InvalidInput("The columns must be in the order in which every column is "
                                   "greater or equal to the preceding one.")


    @classmethod
    def set_schedule_tz(cls, schedule, to_tz, from_tz= None):
        schedule = schedule.copy()
        for col in schedule:
            if from_tz is False:
                schedule[col] = schedule[col].dt.tz_localize(None).dt.tz_localize(to_tz)
                continue

            try:
                schedule[col] = schedule[col].dt.tz_convert(to_tz)
            except TypeError as e:
                if from_tz is None:
                    raise TimeZoneException("If columns are not tz-aware, you need to pass from_tz") from e
                schedule[col] = schedule[col].dt.tz_localize(from_tz).dt.tz_convert(to_tz)
        return schedule

    @staticmethod
    def tDelta(t):
        return pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)

    def __init__(self, schedule=None, frequency=None, start=True, end=False, **kwargs):
        """



        """
        self._freq = None if frequency is None else pd.Timedelta(frequency)

        if not (start in self._valid_start_end and end in self._valid_start_end):
            raise InvalidConfiguration("start and end can only be True, False or 'cross'")

        _vals = kwargs.values()
        if not all([x in ("start", "end", False) for x in kwargs.values()]):
            raise InvalidConfiguration("market_times borders must be 'start', 'end' or False")

        self.start = start
        self.end = end

        self._aligns = kwargs
        self._adj = (self.start is not False or self.end != "cross" or any((x == "end" for x in _vals)))
        self._align = any(_vals)

        self.schedule = schedule # see @schedule.setter

    use = __init__

    @contextmanager
    def use_now(self, schedule, frequency, start=True, end=False, **kwargs):
        original_settings = self.settings
        original_schedule = self.schedule.copy()  # keeping it seperate from settings to avoid recalculation
        original_tz = self.schedtz
        frm = self.__frm
        to = self.__to
        self.use(schedule=schedule, frequency=frequency, start=start, end=end, **kwargs)
        yield
        self.use(schedule=None, **original_settings)  # passing None and setting it directly,
        self._schedule = original_schedule  # bypasses the calculation
        self.schedtz = original_tz
        self.__frm = frm
        self.__to = to

    @property
    def settings(self):
        return dict(frequency=self._freq, start=self.start, end=self.end, **self._aligns)

    @property
    def schedule(self): return self._schedule

    @schedule.setter
    def schedule(self, schedule):
        self.clear()
        if schedule is None:
            self.schedtz = self.SCHEDTZ
            self._schedule = pd.DataFrame(columns=["real", "start", "end", "session"])
            self.__frm = self.__to =  self._some_date
        else:
            self._verify_schedule(schedule)
            if schedule.columns[0] in self._aligns or "break_end" in self._aligns:
                raise InvalidConfiguration("Sessions start cannot be borders")

            self.schedtz = schedule.iloc[:, 0].dt.tz
            self._schedule = self._create_sessions_and_parts(schedule)
            self.__frm = self.schedule.real.iat[0]
            self.__to = self.schedule.end.iat[-1]

    @property
    def frequency(self):
        if self._freq is None: raise InvalidConfiguration("You never defined a frequency")
        return self._freq

    @frequency.setter
    def frequency(self, frequency):
        self.clear()
        self._freq = pd.Timedelta(frequency)
        self.schedule["start"] = self.schedule.real  # replace calced_starts with real one
        self._adjust_start_inplace(self.schedule)

    def _adjust_start_inplace(self, schedule):
        """adjusts start column and deletes _change column in place"""
        if self._freq is None: return

        if schedule._change.any():  # adjust the start values if any "start"'s were requested
            adj = (schedule.end - schedule.start) % self.frequency  # calc the part left to fill
            adj.loc[adj.ne(self._tdzero)] = self.frequency - adj
            schedule.loc[schedule._change, "start"] = schedule.start - adj  # extend it

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


        all parts/sessions where start == end will be dropped entirely

        :param schedule:
        :return:
        """

        earliest, latest = schedule.columns[[0, -1]]
        parts = []
        for border in schedule.columns:
            option = self._aligns.get(border, False)
            if option or border == "break_start":
                parts.append(schedule[[earliest, border]].copy())
                parts[-1]["_change"] = option == "start"
                earliest = border.replace("break_start", "break_end")  # in case of breaks

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

    def __call__(self, schedule, frequency, start=True, end=False, **kwargs):
        with self.use_now(schedule, frequency, start=start, end=end, **kwargs):
            return pd.DatetimeIndex(self._times(self.__frm, self.__to))

    __call__.__doc__ = __init__.__doc__

    def _check_data_set_sched(self, data, adjclosed):
        if data.isna().any().any():
            raise InvalidInput("Please handle the missing values in the data before using this method")

        inferred_tf = (data.index - data.index.to_series().shift()).mode().iat[0]
        if adjclosed: data.index = data.index - inferred_tf

        if inferred_tf >= self.frequency:
            raise InvalidConfiguration("the timeframe to convert from needs to be smaller than the timeframe "
                                       "to convert to")

        dmin, dmax = data.index[[0, -1]]
        dmax = dmax + inferred_tf
        if dmin < self.__frm or dmax > self.__to:
            raise InvalidInput("Schedule doesn't cover the whole data")

        # _sched is needed by the helper functions
        self._sched = self.schedule[self.schedule.real.ge(dmin) & self.schedule.end.le(dmax)]

        if not (self._sched.real.isin(data.index) &
                self._sched.end.isin(data.index+ inferred_tf)).all():
            raise InvalidInput("You seem to have missing data. This is not refering to NaN values but to "
                               "market times that aren't represented in your data. This may also be because your "
                               "timeframe is too large.")

        dates = data.index.normalize().unique()
        if not (dates.isin(self._sched.real.dt.normalize()) |
                dates.isin(self._sched.end.dt.normalize())).all():
            raise InvalidInput("There is data in the index that is not in the schedule")

        return data, inferred_tf


    def _group_parts_origin(self, data, inferred_tf):
        """
        This method will group the requested parts/sessions in `sched` by
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
        """
        real = self._sched.real.set_axis(self._sched.real)
        real = real - real.dt.normalize()
        end = self._sched.end.set_axis(self._sched.end - inferred_tf)
        end = end - end.dt.normalize()

        origins = self._sched.start.set_axis(real.index).reindex(data.index)

        real = real.reindex(data.index)
        end = end.reindex(data.index)
        data.index = data.index.where(origins.isna(), origins)

        return data.groupby([real.set_axis(data.index).ffill(),
                             end.set_axis(data.index).bfill()])

    def _session_resample(self, part, inferred_tf, label, agg_map):
        """
        This will handle uneven tfs, by splitting into sesssions

        It will prepare the origin of each day, when creating the function, thereby
        eliminating the need to recalculate it at every iteration

        :param firstrows:
        :param agg_map:
        :return:
        """
        try: ix = part[self._srt]
        except KeyError: ix = part.index.to_series()

        starts = (ix - ix.shift()).le(inferred_tf)
        sessions = part.groupby(ix.where(~starts, None).ffill())

        if not part.index[sessions.cumcount().eq(0)].isin(self._sched.real).all():
            raise InvalidInput("There seem to be part starts in the pricedata that are not found in the "
                               "schedule, please make sure the schedule and data match.")

        return sessions.resample(self._freq, origin="start", label=label).agg(agg_map)

    def _convert(self, data, agg_map, label, closed):
        """
        :param data:
        :return:
        """
        even = (self._day % self.frequency) == self._tdzero  # evenly divides day
        data, inferred_tf = self._check_data_set_sched(data, closed != "left")
        if self._align:
            assert not self._srt in data, f"Please rename column: {self._srt}."
            data[self._srt] = data.index # a column with integers showing the original order of the parts
            agg_map[self._srt] = "first"
            parts = self._group_parts_origin(data, inferred_tf)

            if even:
                new = parts.resample(self.frequency, origin="start", label=label
                                      ).agg(agg_map).dropna(how="any")
            else:
                new = parts.apply(self._session_resample, args= (inferred_tf, label, agg_map))

            tx = pd.DatetimeIndex(self._times(*data.index[[0, -1]]))
            new = new.sort_values(self._srt).set_index(tx, drop=True).drop(columns=self._srt)

        elif even:
            new = data.resample(self.frequency, label=label, origin=self._sched.start.iat[0]
                                ).agg(agg_map).dropna(how="any")
        else:
            new = self._session_resample(data, inferred_tf, label, agg_map).droplevel(0).dropna(how="any")

        new.index.freq = None
        return new


    def convert(self, data, freq=None, agg_map=None, closed="left", tz=None):
        """

        :param data: dataframe with datetimeindex to convert
        :param freq: frequency/timeframe to use instead of self.frequency (resulting frequency)
        :param agg_map: dictionary to replace self.default_agg_map if desired
        :param closed: on which side the passed `data` is closed
            (not the returned dataframe, that is determined by the start/end configuration of
             the IndexCalculator instance)
        :param tz: if the datetimeindex of `data` is timezone naive this is the timezone it should
            be interpreted in, will be ignored if the index is timezone aware
        :return: DataFrame with index in `freq` and data converted according to `agg_map`, tzinfo will always be the
            same as the input data
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
            agg_map = self.default_agg_map.copy()
            data.columns = data.columns.str.lower()

        label = "left" if self.start else "right"
        with self._temp(freq):
            new = self._convert(data, agg_map, label, closed).tz_convert(tz)

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