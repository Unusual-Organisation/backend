from datetime import datetime

from peewee import AutoField
from peewee import BooleanField
from peewee import CharField
from peewee import DateTimeField

from uorg.models import BaseModel
from uorg.utils.errors import ConflictError
from uorg.utils.passwords import hash_password


class User(BaseModel):
    """
    The main user model.
    """

    # User's ID (primary key)
    id = AutoField()
    # the user's first name
    first_name = CharField(null=False)
    # The user's last name
    last_name = CharField(null=False)
    # The user's email address
    email = CharField(null=False, unique=True)
    # The user's password, hashed with 'argon2'
    password = CharField(null=False)
    # The user's creation date
    dt_registered = DateTimeField(default=datetime.utcnow)
    # When the user was last modified (by him or an admin)
    dt_last_modified = DateTimeField(default=datetime.utcnow)
    # True if user has its email confirmed. False otherwise
    is_confirmed = BooleanField(default=False)
    # Date when the user was confirmed
    dt_confirmed = DateTimeField(null=True)

    def get_jwt_info(self):
        return {"id": self.id, "email": self.email}

    def to_dict(self, exclude=None, include=None):
        """
        Will return the user as a dict with all the keys from the model, but without the password
        :return:
        """
        if include is None:
            include = {}
        if exclude is None:
            exclude = []
        exclude.append("password")
        returned_dict = super().to_dict(exclude=exclude, include=include)
        return returned_dict

    @staticmethod
    def register(first_name: str, last_name: str, email: str, password: str, is_confirmed: bool = False):
        if User.get_or_none(email=email):
            raise ConflictError("Email taken.")
        enc_password = hash_password(password)
        if is_confirmed:
            dt_confirmed = datetime.utcnow()
        else:
            dt_confirmed = None
        new_user = User.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=enc_password,
            is_confirmed=is_confirmed,
            dt_confirmed=dt_confirmed,
        )
        return new_user
