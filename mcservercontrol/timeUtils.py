import datetime

class TimeUtils:
    LOCAL_TIMEZONE = datetime.datetime.now().astimezone().tzinfo
    @classmethod
    def nowStamp(cls):
        return cls.utcNow().timestamp()

    @staticmethod
    def toStr(dt: datetime.datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def stamp2Local(cls, stamp: float):
        local_datetime = datetime.datetime.fromtimestamp(stamp).replace(tzinfo=cls.LOCAL_TIMEZONE)
        return local_datetime

    @classmethod
    def stamp2Utc(cls, stamp: float):
        return cls.local2Utc(cls.stamp2Local(stamp))
    
    @staticmethod
    def utcNow() -> datetime.datetime:
        return datetime.datetime.now(datetime.timezone.utc)

    @classmethod
    def localNow(cls) -> datetime.datetime:
        return datetime.datetime.now(cls.LOCAL_TIMEZONE)

    @classmethod
    def utc2Local(cls, utc_datetime: datetime.datetime) -> datetime.datetime:
        # https://stackoverflow.com/a/39079819
        return utc_datetime.astimezone(cls.LOCAL_TIMEZONE)

    @classmethod
    def local2Utc(cls, local_datetime: datetime.datetime) -> datetime.datetime:
        return local_datetime.astimezone(datetime.timezone.utc)

    @classmethod
    def utcNowStr(cls) -> str:
        return datetime.datetime.strftime(cls.utcNow(), "%Y-%m-%d %H:%M:%S")

    @classmethod
    def localNowStr(cls) -> str:
        return datetime.datetime.strftime(cls.localNow(), "%Y-%m-%d %H:%M:%S")

    @classmethod
    def strUtcTimeToDatetime(cls, t: str) -> datetime.datetime:
        return datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S").replace(tzinfo = datetime.timezone.utc)

    @classmethod
    def strLocalTimeToDatetime(cls, t: str) -> datetime.datetime:
        return datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S").replace(tzinfo = cls.LOCAL_TIMEZONE)
