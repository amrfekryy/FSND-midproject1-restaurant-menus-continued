
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

class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)

    # relate MenuItem object to Restaurant object through the ForeignKey
    menu_items = relationship("MenuItem")


class MenuItem(Base):
    __tablename__ = 'menu_item'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))

    # relate MenuItem object to Restaurant object through the ForeignKey
    restaurant = relationship("Restaurant")

    @property
    def serialize(self):
        """returns object data in easily serializable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'course': self.course
        }
    

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
