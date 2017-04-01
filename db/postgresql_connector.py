from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class PostgreSQLConnector(object):
    session = None
    engine = None

    def connect(self, engine_string):
        if self.session is None:
            self.engine = create_engine(engine_string)
            Base.metadata.create_all(self.engine)
            session = sessionmaker(bind=self.engine)
            self.session = session()
        return self.session

    def close(self):
        self.session.close()
        self.engine.dispose()