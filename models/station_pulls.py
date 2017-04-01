from sqlalchemy import Column, BIGINT, TIMESTAMP, TEXT, BOOLEAN
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime

from db.postgresql_connector import Base


class StationPulls(Base):
    __tablename__ = 'station_pulls'

    id = Column('id', BIGINT, primary_key=True, unique=True)
    name = Column('name', TEXT)
    lines = Column('lines', ARRAY(TEXT))
    has_machines = Column('has_machines', BOOLEAN)
    is_accessible = Column('is_accessible', BOOLEAN)
    elevator_count_words = Column('elevator_count_words', TEXT)
    escalator_count_words = Column('escalator_count_words', TEXT)
    outages = Column('outages', TEXT)
    accessible_note = Column('accessible_note', TEXT)
    pull_time = Column('pull_time', TIMESTAMP, default=datetime.now())

    def __repr__(self):
        return '<Tweets(user_id={0}, tweet_id={1})>'.format(self.user_id, self.id)
