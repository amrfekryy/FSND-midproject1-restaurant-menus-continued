
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Base, Restaurant, MenuItem

def main():

	# bind to DB and DB tables
	engine = create_engine('sqlite:///restaurantmenu.db')
	Base.metadata.bind = engine

	# establish 'session' connection to allow performing CRUDs
	DBSession = sessionmaker(bind=engine)
	session = DBSession()


	restaurants = session.query(Restaurant).all()
	menu_items = session.query(MenuItem).all()

	print()

	if restaurants == [] and menu_items == []:
		print("Database is empty!")
	else:
		print("Database contents:")
		print()
		
		for index, restaurant in enumerate(restaurants):
			print(f"{index+1}- {restaurant.name}:")
			for index2, item in enumerate(restaurant.menu_items):
				print(f"  {index2+1}- {item.name}")
	print()

if __name__ == '__main__':
	main()
