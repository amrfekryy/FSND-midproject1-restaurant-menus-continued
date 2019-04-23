
# CONFIGURATION-1: 

# import dependencies
import sys
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

# instantiate sqlalchemy base object
Base = declarative_base()

# -------------------------------------------------

# TABLES OOD:
# transform db_design.sql into object oriented design

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    email = Column(String(80), nullable = False)
    picture = Column(String(250))

    menu_items = relationship("MenuItem")
    restaurants = relationship("Restaurant")

    @property
    def serialize(self):
        """returns object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture }


class Restaurant(Base):
    __tablename__ = 'restaurants'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    user_id = Column(Integer, ForeignKey('users.id'))

    menu_items = relationship("MenuItem")
    user = relationship("User")

    @property
    def serialize(self):
        """returns object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id }


class MenuItem(Base):
    __tablename__ = 'menu_items'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    course = Column(String(80), nullable = False)
    description = Column(String(250), nullable = False)
    price = Column(String(10), nullable = False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    restaurant = relationship("Restaurant")
    user = relationship("User")

    @property
    def serialize(self):
        """returns object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'course': self.course,
            'description': self.description,
            'price': self.price,
            'restaurant_id': self.restaurant_id,
            'user_id': self.user_id }


# -------------------------------------------------

# CONFIGURATION-2:

def main():

    # [create and] bind DB to SQLAlchemy engine
    engine = create_engine('sqlite:///restaurantmenu.db')
    # create DB tables based on table classes (Base sub-classes) (declaratives)
    Base.metadata.create_all(engine)

    print()
    print("Database has been setup")
    print()

if __name__ == '__main__':
    main()
