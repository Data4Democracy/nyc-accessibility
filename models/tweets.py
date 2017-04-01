from sqlalchemy import Column, BIGINT, TIMESTAMP, TEXT

from db.postgresql_connector import Base


class Tweets(Base):
    __tablename__ = 'tweets'

    id = Column('id', BIGINT, primary_key=True, unique=True)
    created_at = Column('created_at', TIMESTAMP)
    tweet_text = Column('tweet_text', TEXT)

    def __repr__(self):
        return '<Tweets(user_id={0}, tweet_id={1})>'.format(self.user_id, self.id)