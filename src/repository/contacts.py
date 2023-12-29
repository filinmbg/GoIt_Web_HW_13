from typing import Type

from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_contacts(skip: int, limit: int, db: Session) -> list[Type[Contact]]:
    """
    The get_contacts function returns a list of contacts from the database.

    :param skip: int: Determine how many contacts to skip
    :param limit: int: Limit the number of records returned
    :param db: Session: Pass the database session to the function
    :return: A list of contact objects
    :doc-author: Trelent
    """

    return db.query(Contact).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, db: Session) -> Type[Contact] | None:
    """
    The get_contact function returns a contact object from the database.
        Args:
            contact_id (int): The id of the contact to be retrieved.
            db (Session): A connection to the database.

    :param contact_id: int: Get the contact by id
    :param db: Session: Pass the database session to this function
    :return: A contact object or none if the query fails
    :doc-author: Trelent
    """

    return db.query(Contact).filter(Contact.id == contact_id).first()


async def create_contact(body: ContactModel, db: Session) -> Contact:
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactModel: Get the phone_number from the body of the request
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """

    contact = Contact(phone_number=body.phone_number)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(
    contact_id: int, body: ContactModel, db: Session, user: User
) -> Contact | None:
    """
    The update_contact function updates a contact in the database.
        Args:
            contact_id (int): The id of the contact to update.
            body (ContactModel): The updated ContactModel object with new values for phone number and/or email address.
                Note that only one of these fields can be updated at a time, as they are both unique constraints on the
                table.

    :param contact_id: int: Identify the contact to update
    :param body: ContactModel: Get the new phone number from the request body
    :param db: Session: Pass the database session to the function
    :param user: User: Make sure that the user who is updating
    :return: A contact object
    :doc-author: Trelent
    """

    contact = (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
        .first()
    )
    if contact:
        contact.phone_number = body.phone_number
        db.commit()
    return contact


async def remove_contact(contact_id: int, db: Session, user: User) -> Contact | None:
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be removed.
            db (Session): A connection to the database.  This is passed in by FastAPI, and is used for all
            queries/commits/etc...
            user (User): The current logged-in user, as determined by FastAPI's authentication system.

    :param contact_id: int: Identify the contact to be removed
    :param db: Session: Pass the database session to the function
    :param user: User: Get the user id from the jwt token
    :return: The contact that was removed
    :doc-author: Trelent
    """

    contact = (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
        .first()
    )
    if contact:
        db.delete(contact)
        db.commit()
    return contact