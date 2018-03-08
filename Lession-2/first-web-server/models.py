from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///restaurant.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

class Restaurant(Base):
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    def __repr__(self):
        return '<Restaurant %r>' % self.name

    @staticmethod
    def query(name):
        assert isinstance(name, str)
        return session.query(Restaurant).filter(Restaurant.name == name).first()

    @staticmethod
    def query_by_id(id):
        try:
            id = int(id)
        except ValueError:
            raise ValueError("Cannot convert %s to Integer" % id)
        return session.query(Restaurant).filter(Restaurant.id == id).first()

    @staticmethod
    def query_all():
        return session.query(Restaurant).all()

    @staticmethod
    def rename(id, name):
        r = Restaurant.query_by_id(id)
        r.name = name
        session.add(r)
        session.commit()
        
    @staticmethod
    def insert(name):
        if Restaurant.query(name) is not None:
            raise ValueError("Restaurant %r already exists" % name)
        else:
            res = Restaurant(name=name)
            session.add(res)
            session.commit()

    @staticmethod
    def delete(id):
        r = Restaurant.query_by_id(id)
        if r is None:
            return False
        else:
            session.delete(r)
            session.commit()
            return True


Base.metadata.create_all(engine)
