import json
import os
import random
import threading
import time
from datetime import datetime
from enum import Enum
from functools import reduce, total_ordering
from queue import Queue

import pandas as pd
from log import logger

TRACES_PATH = "./traces"


@total_ordering
class TimeUnit(Enum):
    MINUTE = ("minute", 2)
    HOUR = ("hour", 3)
    DAY_OF_WEEK = ("dow", 4)
    DAY_OF_MONTH = ("dom", 4)
    DAY_OF_YEAR = ("doy", 4)

    def __new__(cls, member_value, member_order):
        member = object.__new__(cls)
        member._value_ = member_value
        member.order = member_order
        return member

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.order < other.order
        return NotImplemented

    def __str__(self):
        return self.value


class Trace:
    def __init__(
        self,
        name: str,
        topic: str,
        filename: str,
        noise_factor: float,
        match_timestamp_by: str = "minute",
        target_value: str = "value",
    ) -> None:
        self.name = name
        self.topic = topic
        self.filename = filename
        self.noise_factor = noise_factor
        self.match_timestamp_by = TimeUnit(match_timestamp_by)
        self.target_value = target_value

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class Parser:
    def __init__(self) -> None:
        pass

    def parse(
        self,
        filename: str,
        datetime: datetime,
        time_unit: TimeUnit,
        noise_factor: float,
        topic: str,
        target_value: str = "value",
    ) -> pd.Series:
        logger.info(f"Parsing file {filename}")
        data = pd.read_csv(
            os.path.join(TRACES_PATH, filename),
            parse_dates=["timestamp"],
            infer_datetime_format=True,
        )
        filters = self._get_filters_criteria(data, datetime, time_unit)
        # Apply filters
        data: pd.Series = data.loc[reduce(lambda a, b: a & b, filters)]
        # Transform to dict
        data = data.to_dict(orient="records")
        # Get only one read and add noise and topic
        if data:
            data = data[0]
            data["value"] = random.gauss(data[target_value], noise_factor)
            data["topic"] = topic
            data["timestamp"] = datetime.isoformat()
        return data

    @staticmethod
    def _get_filters_criteria(df: pd.DataFrame, datetime: datetime, criteria: str):
        filters = [df["timestamp"].dt.minute == datetime.time().minute]
        if criteria > TimeUnit.HOUR:
            filters.append(df["timestamp"].dt.hour == datetime.time().hour)
        if criteria == TimeUnit.DAY_OF_WEEK:
            filters.append(
                df["timestamp"].dt.day_of_week == datetime.timetuple().tm_wday
            )
        if criteria == TimeUnit.DAY_OF_MONTH:
            filters.append(df["timestamp"].dt.day ==
                           datetime.timetuple().tm_mday)
        if criteria == TimeUnit.DAY_OF_YEAR:
            filters.append(
                df["timestamp"].dt.day_of_year == datetime.timetuple().tm_yday
            )
        return filters


class Scheduler:
    def __init__(self, queue: Queue) -> None:
        self._stop_flag = False
        # Initiate the queue client to start sending data
        self.queue = queue
        # Load parser
        self.parser = Parser()
        # Load traces
        self.threads = []

    def start(self):
        logger.info("Starting scheduler")
        self.load_traces()

    def stop(self):
        logger.info("Stopping scheduler")
        self._stop_flag = True

    def load_traces(self):
        try:
            with open(os.path.join(TRACES_PATH, "traces.json"), "r") as f:
                traces = [Trace(**trace) for trace in json.load(f)["traces"]]
                for trace in traces:
                    t = threading.Thread(
                        target=self.simulate_trace, args=(trace,))
                    self.threads.append(t)
                    t.start()
        except FileNotFoundError:
            logger.error("No traces file found")
            exit(1)

    def simulate_trace(self, trace: Trace):
        while not self._stop_flag:
            now = datetime.now()
            data = self.parser.parse(
                trace.filename,
                datetime=now,
                time_unit=trace.match_timestamp_by,
                noise_factor=trace.noise_factor,
                topic=trace.topic,
                target_value=trace.target_value,
            )
            if data:
                data = json.dumps(data, default=str)
                self.queue.put(data)
                logger.info(f"Enqueuing {data}")
            else:
                logger.info(f"No data for {trace.name} at {now}")
            time.sleep(60)
