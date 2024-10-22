from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import DateTime, Column
from sqlalchemy.types import TypeDecorator
import pytz
from datetime import datetime

# Custom TypeDecorator for timezone-aware DateTime
class AwareDateTime(TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and value.tzinfo is not None:
            # Convert to UTC before saving to the database
            return value.astimezone(pytz.utc)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            # Convert from UTC to desired timezone when retrieving from the database
            tz = pytz.timezone('Europe/Moscow')
            return value.astimezone(tz)
        return value

# Custom base class
class CustomBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __init_subclass__(cls):
        super().__init_subclass__()
        # Replace DateTime columns with AwareDateTime
        for key, value in cls.__dict__.items():
            if isinstance(value, Column) and isinstance(value.type, DateTime):
                value.type = AwareDateTime()

Base = declarative_base(cls=CustomBase)
