# Flask_RESTful_API_jwt_app

## Libraries Used

- click==7.1.2
- Flask==1.1.2
- Flask-JWT==0.3.2
- Flask-SQLAlchemy==2.5.1
- greenlet==1.0.0
- itsdangerous==1.1.0
- Jinja2==2.11.3
- MarkupSafe==1.1.1
- PyJWT==1.4.2
- SQLAlchemy==1.4.11
- Werkzeug==1.0.1


## Build the Application
**Basics**
- Clone the repository
- Activate virtualenv
- Install the requirements

**Create DB**

From your terminal follow the command. 
```
python create_db.py
```
## Run the Application
From your terminal follow the command. 
```
python app.py
```
## Use the Application

**Homepage**

- Open Postman
- Type URL provided by the Flask Application and click "Send"
- We are on home route

**Login**

- In postman open "Authorization" tab
- Select "Basic Auth" type of Authorization.
- Type username = "ADMIN" and password = "12345".
- Type "/login" in front of the base url and click "Send"
- In the Response section we receive a token.
- Copy that token.
- Open "Headers" tab and type in new header provide, key = "login_token", value = token

**Users**

###### View all users

- Type "/user" in front of the base url, select method = "GET" and click "Send"

###### View single user

- Type "/user/<user_id>" in front of the base url, select method = "GET" and click "Send"

###### Add new user

- Open "Body" tab and in the "raw" section select "json" type
- Type json response in the body.

```
{"name" : "abc", "password" : "12345" }
```
- Type "/user" in front of the base url, select method = "POST" and click "Send"

###### Promote existing user as ADMIN

- Type "/user/<user_id>" in front of the base url, select method = "PUT" and click "Send"

###### Delete user

- Type "/user/<user_id>" in front of the base url, select method = "DELETE" and click "Send"

###### Note

Only ADMIN user can handle user related API's

**Books**
