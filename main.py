from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uuid
import string
import secrets
import datetime
import json


app = FastAPI()


user_db = []

class RegisterUser(BaseModel):
    name: str
    email: str


def current_time():
    local_time = datetime.datetime.now()

    clean_time = local_time.strftime("%Y-%m-%d %H:%M:%S")

    return clean_time

# Profile ID is for client view
def create_profile_id():

    chars = string.ascii_letters + string.digits

    while True:
        profile_id = "".join(secrets.choice(chars) for _ in range(5))

        try:
            with open("user_db.json", "r+") as json_file:
                users = json.load(json_file)

                for user in users:
                    if user["profile_id"] == profile_id:
                        break
                else:
                    return profile_id
        except (FileNotFoundError, json.JSONDecodeError):
            return profile_id

def add_user_db(user_data):
    user = {
        "id": user_data["id"],
        "profile_id": user_data["profile_id"],
        "name": user_data["name"],
        "email": user_data["email"],
        "createdAt": current_time()
    }

    try:
        with open("user_db.json", "r") as json_file:
            users = json.load(json_file)

    except (FileNotFoundError, json.JSONDecodeError):
        users = []

    for existing_user in users:
        if existing_user["email"] == user["email"]:
            raise ValueError("User Already Exists")

    users.append(user)

    with open("user_db.json", "w") as json_file:
        json.dump(users, json_file, indent=4)


@app.post("/new-user")
def new_user(user: RegisterUser):

    profile_id = create_profile_id()

    add_user = {
        "id" : uuid.uuid4().hex,
        'profile_id' : profile_id,
        "name": user.name,
        "email": user.email
    }

    try:
        add_user_db(add_user)
    except ValueError:
        raise HTTPException(
            status_code=409,
            detail="User Already Exists"
        )

    return {
        "profile_id" : profile_id, 
        "name" : user.name,
        "status" : "Profile created successfully"
    }


@app.get("/")
def health_check():
    return {
        "status" : "running"
    }
