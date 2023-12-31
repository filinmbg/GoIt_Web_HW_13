from datetime import datetime, timedelta
from typing import Optional


from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.conf.config import settings
from src.database.db import get_db
from src.repository import users as repository_users


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    # r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and hashed password as arguments.
        It then uses the pwd_context object to verify that the plain-text password matches the hashed
        password.

        :param self: Represent the instance of the class
        :param plain_password: Store the password that is entered by the user
        :param hashed_password: Compare the password that is being passed in with the hashed version of it
        :return: True if the password is correct and false if it is not
        :doc-author: Trelent
        """

        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
        The function uses the pwd_context object to generate a hash from the given password.

        :param self: Access the attributes and methods of a class
        :param password: str: Get the password from the user
        :return: A hash of the password
        :doc-author: Trelent
        """

        return self.pwd_context.hash(password)

    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        The create_access_token function creates a new access token.
            Args:
                data (dict): A dictionary of key-value pairs to include in the JWT payload.
                expires_delta (Optional[float]): An optional expiration time, in seconds, for the access token. Defaults to 15 minutes if not provided.

        :param self: Represent the instance of the class
        :param data: dict: Store the data that will be encoded in the jwt
        :param expires_delta: Optional[float]: Set the expiration time of the access token
        :return: A token that expires in 15 minutes
        :doc-author: Trelent
        """

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        The create_refresh_token function creates a refresh token for the user.
            Args:
                data (dict): A dictionary containing the user's id and username.
                expires_delta (Optional[float]): The time in seconds until the token expires. Defaults to None, which sets it to 7 days from now.

        :param self: Represent the instance of the class
        :param data: dict: Pass in the user's id, username and email
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: A refresh token that is encoded using the jwt library
        :doc-author: Trelent
        """

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
    ):
        """
        The get_current_user function is a dependency that will be used in the
            protected endpoints. It takes a token as an argument and returns the user
            associated with that token. If no user is found, it raises an HTTPException.

        :param self: Represent the instance of a class
        :param token: str: Get the token from the authorization header
        :param db: Session: Get the database session
        :return: A user object that is used to authenticate the request
        :doc-author: Trelent
        """

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") == "access_token":
                email = payload.get("sub")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.find_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function is used to decode the refresh token.
        It will raise an exception if the token is invalid or has expired.

        :param self: Represent the instance of the class
        :param refresh_token: str: Pass the refresh token to the function
        :return: The email of the user associated with the refresh token
        :doc-author: Trelent
        """

        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    def create_email_token(self, data: dict):  # для верифікації
        """
        The create_email_token function creates a token that is used to verify the user's email address.
        The function takes in a dictionary of data, and adds an iat (issued at) timestamp, an exp (expiration) timestamp 7 days from now, and a scope of &quot;email_token&quot;.
        It then encodes this data using the SECRET_KEY and ALGORITHM defined in our config file.
        This encoded string is returned as the token.

        :param self: Make the function a method of the class
        :param data: dict: Pass in the data that will be encoded
        :return: A token that is used to verify the user's email
        :doc-author: Trelent
        """

        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"}
        )
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email address associated with that token.
        It does this by decoding the JWT using our SECRET_KEY and ALGORITHM, then checking to make sure that it has a scope of &quot;email_token&quot;.
        If so, it returns the email address from the sub field in its payload. If not, or if there is any other error during decoding (such as an invalid signature),
        it raises an HTTPException.

        :param self: Represent the instance of the class
        :param token: str: Pass in the token that is sent to the user's email
        :return: The email that was encoded in the token
        :doc-author: Trelent
        """

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "email_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )


auth_service = Auth()