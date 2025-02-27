import datetime

from sqlobject import DateTimeCol, IntCol, SQLObject


class Session(SQLObject):
    """
    SQLObject model for reading sessions.

    Attributes:
        date (DateTimeCol): The date and time of the reading session
        duration (IntCol): The duration of the reading session in minutes
    """

    date = DateTimeCol(default=datetime.datetime.now)
    duration = IntCol(default=0)

    def __repr__(self):
        return f"<Session id={self.id}, date={self.date}, duration={self.duration}>"
