from typing import List

from fastapi_limiter.depends import RateLimiter  # для обмеження кількості запитів

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.schemas import UserModel, UserResponse, UserResponseGet
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=List[UserResponseGet],
    description="No more than 2 requests per 5 seconds",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_users function returns a list of users.

    :param skip: int: Skip the first n number of users
    :param limit: int: Limit the number of users returned
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :param : Get the current user
    :return: A list of users
    :doc-author: Trelent
    """

    users = await repository_users.get_users(skip, limit, db)
    return users


@router.get(
    "/{user_id}",
    response_model=UserResponseGet,
    description="No more than 2 requests per 5 seconds",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_user function is a GET endpoint that returns the user with the given ID.
    It requires an authenticated user, and it will return 404 if no such user exists.

    :param user_id: int: Get the user_id from the path
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user
    :param : Get the user id from the path of the request
    :return: A user object
    :doc-author: Trelent
    """

    user = await repository_users.get_user(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


# Тепер контакт додається тільки під час SignUp
# @router.post("/", response_model=UserResponse)
# async def create_user_by_user(body: UserModel, db: Session = Depends(get_db)):
#     return await repository_users.create_user(body, db)
# ---------------


@router.put(
    "/{user_id}",
    response_model=UserResponseGet,
    description="No more than 2 requests per 5 seconds",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def update_user(
    body: UserModel,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The update_user function updates a user in the database.
    It takes an id, and a body containing the updated information for that user.
    The function returns the updated user object.

    :param body: UserModel: Get the data from the request body
    :param user_id: int: Get the user_id from the url
    :param db: Session: Get the database session
    :param current_user: User: Check if the user is an admin or not
    :param : Get the user id from the url
    :return: A usermodel object
    :doc-author: Trelent
    """

    user = await repository_users.update_user(user_id, body, db, current_user)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.delete(
    "/{user_id}",
    response_model=UserResponseGet,
    description="No more than 2 requests per 5 seconds",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def remove_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The remove_user function removes a user from the database.

    :param user_id: int: Specify the user id of the user to be deleted
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user
    :param : Get the user_id from the path
    :return: The user object that was removed
    :doc-author: Trelent
    """

    user = await repository_users.remove_user(user_id, db, current_user)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get(
    "/user_name/",
    response_model=UserResponseGet,
    description="No more than 2 requests per 5 seconds",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def find_user_by_name(
    user_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The find_user_by_name function is a GET request that returns the user with the given name.
    If no user exists, it will return a 404 error.

    :param user_name: str: Specify the name of the user that we want to find
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :param : Get the current user
    :return: A user object
    :doc-author: Trelent
    """

    if user_name:
        user = await repository_users.find_user_by_name(user_name, db)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user


@router.get(
    "/user_last_name/",
    response_model=UserResponseGet,
    description="No more than 2 requests per 5 seconds",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def find_user_by_last_name(
    user_last_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The find_user_by_last_name function is a GET request that returns the user with the specified last name.
    If no user is found, it will return a 404 error.

    :param user_last_name: str: Specify the last name of the user we want to find
    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the current user
    :param : Get the current user from the database
    :return: A user object
    :doc-author: Trelent
    """

    if user_last_name:
        user = await repository_users.find_user_by_last_name(user_last_name, db)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user


@router.get(
    "/user_email/",
    response_model=UserResponseGet,
    description="No more than 2 requests per 5 seconds",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def find_user_by_email(
    user_email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The find_user_by_email function is a GET request that takes in an email address and returns the user associated with it.
    If no user is found, then a 404 error will be returned.

    :param user_email: str: Find the user by email
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :param : Get the user_id from the path
    :return: A user object
    :doc-author: Trelent
    """

    if user_email:
        user = await repository_users.find_user_by_email(user_email, db)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user


@router.get(
    "/next_7_days_birthdays/",
    response_model=List[UserResponseGet],
    description="No more than 2 requests per 5 seconds",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def find_next_7_days_birthdays(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The find_next_7_days_birthdays function returns a list of users who have birthdays in the next 7 days.


    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :param : Get the database session
    :return: A list of users with birthdays in the next 7 days
    :doc-author: Trelent
    """

    user = await repository_users.find_next_7_days_birthdays(db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No birthdays in next 7 days"
        )
    return user


# --------------------оновлення аватара користувача
@router.get("/me/", response_model=UserResponseGet)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_me function is a GET endpoint that returns the current user's information.
    It uses the auth_service to get the current user, and then returns it.

    :param current_user: User: Get the current user
    :return: The current user object, which is the same as the one that was passed to it
    :doc-author: Trelent
    """

    return current_user


@router.patch("/avatar", response_model=UserResponseGet)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The update_avatar_user function updates the avatar of a user. Args: file (UploadFile): The image to be uploaded.
    current_user (User): The user whose avatar is being updated. This is passed in by the auth_service dependency,
    which uses JWT tokens to authenticate users and get their data from the database. It's also used as an argument
    for update_avatar() in repository/users/crud, where it's used to find a specific user by email address and update
    their avatar URL with src_url, which is returned at the end of this function

    :param file: UploadFile: Get the file from the request
    :param current_user: User: Get the current user, and the db: session parameter is used to access
    :param db: Session: Connect to the database
    :return: The user object
    :doc-author: Trelent
    """

    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    public_id = f"web13/{current_user.name}"
    r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    src_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=r.get("version")
    )
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user