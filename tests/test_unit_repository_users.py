import unittest
from unittest.mock import MagicMock

from pydantic import BaseModel, Field, EmailStr

from libgravatar import Gravatar
from typing import Type
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import User, Contact
from src.schemas import UserModel
from src.repository.users import (
    create_user,
    get_users,
    get_user,
    remove_user,
    update_user,
    find_user_by_name,
    find_user_by_last_name,
    find_user_by_email,
    find_next_7_days_birthdays,
    update_token,
    update_avatar,
    confirmed_email,
)


class TestUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.refresh_token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
            ".eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ"
            ".SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )  # example of refresh_token
        self.url = "https://test_url.com"
        self.email = "example@gmail.com"

    async def test_create_user(self):
        body = UserModel(
            name="tests",
            last_name="tests",
            day_of_born="2023-09-02",
            email="exemple@gmail.com",
            description="tests description",
            password="testPassword",
            contacts=[1, 2],
        )
        contacts = [Contact(id=1), Contact(id=2)]
        self.session.query().filter().all.return_value = contacts
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.day_of_born, body.day_of_born)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.description, body.description)
        self.assertEqual(result.password, body.password)
        self.assertEqual(result.contacts, contacts)
        self.assertTrue(
            hasattr(result, "id")
        )  # перевірка на унікальність "id" при створенні

    async def test_get_users(self):
        users = [User(), User(), User()]
        self.session.query().offset().limit().all.return_value = users
        result = await get_users(skip=0, limit=10, db=self.session)
        self.assertEqual(result, users)

    async def test_get_user_found(self):
        self.session.query().filter().first.return_value = self.user
        result = await get_user(user_id=1, db=self.session)
        self.assertEqual(result, self.user)

    async def test_get_user_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user(user_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_remove_user_found(self):
        self.session.query().filter().first.return_value = self.user
        result = await remove_user(user_id=1, db=self.session, user=self.user)
        self.assertEqual(result, self.user)

    async def test_remove_user_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_user(user_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_user_found(self):
        body = UserModel(
            name="tests",
            last_name="tests",
            day_of_born="2023-09-02",
            email="exemple@gmail.com",
            description="tests description",
            password="testPassword",
            contacts=[1, 2],
        )
        contacts = [Contact(id=1), Contact(id=2)]
        user = User(contacts=contacts)
        self.session.query().filter().first.return_value = user
        self.session.commit.return_value = None
        result = await update_user(
            user_id=1, body=body, user=self.user, db=self.session
        )
        self.assertEqual(result, user)

    async def test_update_user_not_found(self):
        body = UserModel(
            name="tests",
            last_name="tests",
            day_of_born="2023-09-02",
            email="exemple@gmail.com",
            description="tests description",
            password="testPassword",
            contacts=[1, 2],
        )
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_user(
            user_id=1, body=body, user=self.user, db=self.session
        )
        self.assertIsNone(result)

    async def test_find_user_by_name_found(self):
        self.session.query().filter().first.return_value = self.user
        result = await find_user_by_name(user_name="test_name", db=self.session)
        self.assertEqual(result, self.user)

    async def test_find_user_by_name_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await find_user_by_name(user_name="test_name", db=self.session)
        self.assertIsNone(result)

    async def test_find_user_by_last_name_found(self):
        self.session.query().filter().first.return_value = self.user
        result = await find_user_by_last_name(
            user_last_name="test_last_name", db=self.session
        )
        self.assertEqual(result, self.user)

    async def test_find_user_by_last_name_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await find_user_by_last_name(
            user_last_name="test_last_name", db=self.session
        )
        self.assertIsNone(result)

    async def test_find_user_by_email_found(self):
        self.session.query().filter().first.return_value = self.user
        result = await find_user_by_email(user_email=self.email, db=self.session)
        self.assertEqual(result, self.user)

    async def test_find_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await find_user_by_email(user_email=self.email, db=self.session)
        self.assertIsNone(result)

    async def test_find_next_7_days_birthdays_found(self):
        users = [User(), User(), User()]
        self.session.query().filter().all.return_value = users
        result = await find_next_7_days_birthdays(db=self.session)
        self.assertEqual(result, users)

    async def test_find_next_7_days_birthdays_not_found(self):
        self.session.query().filter().all.return_value = None
        result = await find_next_7_days_birthdays(db=self.session)
        self.assertIsNone(result)

    async def test_update_token(self):
        await update_token(
            user=self.user, refresh_token=self.refresh_token, db=self.session
        )
        self.assertEqual(self.user.refresh_token, self.refresh_token)

    async def test_update_avatar(self):
        result = await update_avatar(email=self.email, url=self.url, db=self.session)
        self.assertEqual(result.avatar, self.url)

    async def test_confirmed_email(self):
        user = User(email=self.email)
        self.session.query().filter().first.return_value = user
        await confirmed_email(email=self.email, db=self.session)
        self.assertEqual(user.confirmed, True)


if __name__ == "__main__":
    unittest.main()