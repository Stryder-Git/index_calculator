

class PrepException(Exception): pass


class InvalidConfiguration(PrepException): pass
class TimeZoneException(PrepException): pass
class InvalidInput(PrepException): pass
class InvalidTimeFrame(PrepException): pass