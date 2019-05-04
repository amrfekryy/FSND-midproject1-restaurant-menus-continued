# [FSND](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004) mid-project1 - Restaurant Menus

This project is an extension to the flask application in an [earlier project](https://github.com/Amr-Fekry/FSND-midproject1-restaurant-menus). It takes it from a very basic application that is only capable of performing CRUD operations on a database, and adds multiple features leveraging the following technologies:

1. OAuth2 Providers:
The app resources are protected using a login system that depends on third-party authentication providers like Google and Facebook. It also has a local permission system that controls the user-experience and only allow a user to perform CRUD operations on resources created by him.

2. RESTful APIs:
The app has its own API endpoints that allow external requests to collect information from the app's database. It also provides the _Worldwide_ search feature that leverages third-party published APIs to get information about restaurants around the world.

3. Bootstrap:
The app was aesthetically improved using some bootstrap components.


#### Running the app:
You can check out the deployed version of the app on heroku [here](https://restaurants-and-menus.herokuapp.com/), or follow the next steps to run the app locally:

-  [Python3](https://www.python.org/downloads/) is required.
- clone/download the repsitory and `cd` into it.
- Install external dependencies: `pip3 install -r requirements.txt`
- setup and populate the database: `python db_prepare.py`
- run the app: `python app.py`

#### Future Plans:
- add a local authentication system to register/login users aside from third-party OAuth providers.
- enable using app's API endpoints to perform all CRUD operations on a specific user's resources after a permission is granted from user.
- improve the _Worldwide_ search feature (maybe leveraging google maps API)
- improve app's aesthetics and user experience in general
