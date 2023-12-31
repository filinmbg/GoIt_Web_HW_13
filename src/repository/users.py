from typing import Type
from libgravatar import Gravatar
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date, timedelta
from src.database.models import User, Contact
from src.schemas import UserModel


async def get_users(skip: int, limit: int, db: Session) -> list[Type[User]]:
    """
    The get_users function returns a list of users from the database.

    :param skip: int: Skip a number of records
    :param limit: int: Limit the number of results returned
    :param db: Session: Pass the database session to the function
    :return: A list of user objects
    :doc-author: Trelent
    """

    return db.query(User).offset(skip).limit(limit).all()


async def get_user(user_id: int, db: Session) -> Type[User] | None:
    """
    The get_user function takes in a user_id and db session, and returns the User object with that id.
    If no such user exists, it returns None.

    :param user_id: int: Pass the user_id to the function
    :param db: Session: Pass in the database session
    :return: The user object corresponding to the user_id
    :doc-author: Trelent
    """

    return db.query(User).filter(User.id == user_id).first()


async def remove_user(user_id: int, db: Session, user: User) -> User | None:
    """
    The remove_user function removes a user from the database.
        Args:
            user_id (int): The id of the user to be removed.
            db (Session): A connection to the database.

    :param user_id: int: Identify the user to be removed
    :param db: Session: Access the database
    :param user: User: Check if the user is an admin
    :return: The user that was removed from the database, or none if no user was found
    :doc-author: Trelent
    """

    user = db.query(User).filter(and_(User.id == user_id, User.id == user.id)).first()
    if user:
        db.delete(user)
        db.commit()
    return user


async def update_user(
    user_id: int, body: UserModel, db: Session, user: User
) -> User | None:
    """
    The update_user function updates a user in the database.
        Args:
            user_id (int): The id of the user to update.
            body (UserModel): The updated data for the specified User.

    :param user_id: int: Identify the user to be updated
    :param body: UserModel: Get the data from the request body
    :param db: Session: Access the database
    :param user: User: Get the user who is logged in
    :return: The updated user
    :doc-author: Trelent
    """

    user = db.query(User).filter(and_(User.id == user_id, User.id == user.id)).first()
    if user:
        phones = db.query(Contact).filter(Contact.id.in_(body.contacts)).all()
        user.name = body.name
        user.last_name = body.last_name
        user.day_of_born = body.day_of_born
        user.email = body.email
        user.description = body.description
        user.phones = phones
        db.commit()
    return user


async def find_user_by_name(user_name: str, db: Session) -> Type[User] | None:
    """
    The find_user_by_name function takes in a user_name and db as parameters.
    It then returns the first instance of User that matches the given user_name.

    :param user_name: str: Specify the name of the user that we want to find
    :param db: Session: Pass the database session to the function
    :return: The first user in the database with a given name
    :doc-author: Trelent
    """

    return db.query(User).filter(User.name == user_name).first()


async def find_user_by_last_name(user_last_name: str, db: Session) -> Type[User] | None:
    """
    The find_user_by_last_name function takes in a user's last name and returns the first user with that last name.
        Args:
            user_last_name (str): The last name of the desired User object.
            db (Session): A database session to query for Users.

    :param user_last_name: str: Filter the database by last name
    :param db: Session: Pass in the database session
    :return: The first user with the given last name
    :doc-author: Trelent
    """

    return db.query(User).filter(User.last_name == user_last_name).first()


async def find_user_by_email(user_email: str, db: Session) -> Type[User] | None:
    """
    The find_user_by_email function takes in a user_email and db as parameters.
    It then queries the database for a User object with an email that matches the user_email parameter.
    If it finds one, it returns that User object; otherwise, it returns None.

    :param user_email: str: Specify the email of the user we are looking for
    :param db: Session: Pass the database session object to the function
    :return: A user object if the email exists in the database, otherwise it returns none
    :doc-author: Trelent
    """

    return db.query(User).filter(User.email == user_email).first()


async def find_next_7_days_birthdays(db: Session) -> list[Type[User]] | None:
    """
    The find_next_7_days_birthdays function finds all users who have birthdays in the next 7 days.

    :param db: Session: Pass the database session to the function
    :return: A list of user objects
    :doc-author: Trelent
    """

    today_date = date.today() + timedelta(days=1)
    seventh_day_date = today_date + timedelta(days=7)
    return (
        db.query(User)
        .filter(
            (
                func.date_part("month", User.day_of_born)
                == today_date.month | seventh_day_date.month
            )
            & (func.date_part("day", User.day_of_born) >= today_date.day)
            & (func.date_part("day", User.day_of_born) <= seventh_day_date.day)
        )
        .all()
    )


# -------------------Авторизаційні функції-----------------
async def create_user(body: UserModel, db: Session) -> User:
    """
    The create_user function creates a new user in the database.

    :param body: UserModel: Get the data from the request body
    :param db: Session: Access the database
    :return: The created user
    :doc-author: Trelent
    """

    contacts = db.query(Contact).filter(Contact.id.in_(body.contacts)).all()
    avatar = None  # надамо автоматичну аватарку користувачу через Gravatar
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(
        name=body.name,
        last_name=body.last_name,
        day_of_born=body.day_of_born,
        email=body.email,
        description=body.description,
        password=body.password,
        contacts=contacts,
        avatar=avatar,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, refresh_token, db: Session):
    """
    The update_token function updates token.

    :param user: User: Get the data from the request body
    :param refresh_token: Update the refresh_token in the database
    :param db: Session: Access the database
    :return: The user
    :doc-author: Trelent
    """

    user.refresh_token = refresh_token
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user in the database.

    :param email: Find the user in the database
    :param url: str: Specify the type of data that will be passed into the function
    :param db: Session: Pass the database session into the function
    :return: The user object
    :doc-author: Trelent
    """

    user = await find_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


# ---------Верифікація-----------
async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function confirms the email of a user.

    :param email: str
    :param db: Session: Pass the database session into the function
    """

    user = await find_user_by_email(email, db)
    user.confirmed = True
    db.commit()