# [FSND](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004) mid-project1 - Restaurant Menus

This is an application about restaurants where you can browse through menus created by other users, add your own restaurants and menus, or search for restaurants addresses around the globe.

This project is an extension to a flask application in an [earlier project](https://github.com/Amr-Fekry/FSND-midproject1-restaurant-menus). It takes it from a very basic application that is only capable of performing CRUD operations on a database, and adds multiple features leveraging the following technologies:

1. **OAuth2 Providers**:   
App resources are protected using a login system that depends on third-party authentication providers like Google and Facebook. It also has a local permission system that controls the user-experience and only allow a user to alter resources created by him.

2. **RESTful APIs**:   
The app has fully documented API endpoints that allow external requests to perform all kinds of CRUD operations on the restaurants and menus in our database.   
The app also provides the _Worldwide Search_ feature that leverages third-party published APIs to get information about restaurants around the world. This feature is also supported through the app's API.

3. **Bootstrap**:   
The app was aesthetically improved using many bootstrap components.


### Running the app:
You can check out the deployed version of the app on heroku [here](https://restaurants-and-menus.herokuapp.com/), or follow the next steps to run the app locally:

-  [Python3](https://www.python.org/downloads/) is required.
- clone/download the repsitory and `cd` into it.
- Install external dependencies: `pip3 install -r requirements.txt`
- setup and populate the database: `python db_prepare.py`
- run the app: `python app.py`

### Future Plans:
- Add a local authentication system to register/login users aside from third-party OAuth providers.
- Secure API endpoints to only allow a request to alter a resource created by a user based on the user authorization.
- I am thinking of integrating Google Maps to improve the _Worldwide Search_ feature.
