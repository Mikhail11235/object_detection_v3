import fastapi
from database import DB

app = fastapi.FastAPI()


@app.get("/hello")
async def root():
    return {"message": "Hello World"}


@app.post("/sign_up")
async def root(firstname: str = "", lastname: str = "", password: str = ""):
    db_model = DB()
    res1 = db_model.insert("users", {"firstname": firstname, "lastname": lastname})
    if not res1:
        print("DB error")
        return {"message": "Error: try again later"}
    else:
        res2 = db_model.insert("user_password", {"user_id": res1, "password": password})
        if not res2:
            db_model.delete("users", res1)
            print("DB error")
            return {"message": "Error: try again later"}
        return {"message": "User %s %s was signed up. id: %d" % (firstname, lastname, res1)}
