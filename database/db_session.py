
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from db_setup import Base, Restaurant, MenuItem, User

# connect to DB, tables, and create session
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
session = scoped_session(sessionmaker(bind=engine))
