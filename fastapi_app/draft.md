@app.post("/api/register", status_code=status.HTTP_200_CREATED)
async def register_user(user: User):
    # Implement user registration logic here
    # You can insert the user data into the database

    # Example: Insert the user into a 'users' table
    query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    values = (user.username, user.password)

    cursor = db_connection.cursor()
    cursor.execute(query, values)
    db_connection.commit()
    cursor.close()

    return {"message": "User registered successfully"}


@app.post("/api/login")
async def login_user(user: User):
    # Implement user login authentication logic here
    # You can check the provided username and password against the database

    # Example: Check the username and password in the 'users' table
    query = "SELECT username, password FROM users WHERE username = %s AND password = %s"
    values = (user.username, user.password)

    cursor = db_connection.cursor()
    cursor.execute(query, values)
    result = cursor.fetchone()
    cursor.close()

    if result:
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login failed")

class User(BaseModel):
    username: str
    password: str
