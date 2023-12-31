import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from src.database.models import Contact, User
from src.schemas import ContactModel
from src.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    update_contact,
    remove_contact,
)


class TestUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(phone_number="0632428185")
        result = await create_contact(body=body, db=self.session)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertTrue(
            hasattr(result, "id")
        )  # перевірка на унікальність "id" при створенні

    async def test_update_contact_found(self):
        body = ContactModel(phone_number="0632428185")
        contact = Contact(phone_number=body.phone_number)
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(
            contact_id=1, body=body, user=self.user, db=self.session
        )
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactModel(phone_number="0632428185")
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(
            contact_id=1, body=body, user=self.user, db=self.session
        )
        self.assertIsNone(result)

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, db=self.session, user=self.user)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()