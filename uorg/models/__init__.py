from peewee import Model
from playhouse.shortcuts import model_to_dict

from uorg import uorg_db


class BaseModel(Model):
    class Meta:
        database = uorg_db  # type: ignore

    def to_dict(self, exclude=None, include=None):
        """
        This base method is made to be overridden when you need something removed to added to the returned dictionary
        See for example https://github.com/Seluj78/PyMatcha/blob/dev/backend/PyMatcha/models/user.py#L204-L228
        """
        if include is None:
            include = {}
        if exclude is None:
            exclude = []
        returned_dict = model_to_dict(self)
        for i in exclude:
            returned_dict.pop(i)
        for key, value in include.items():
            returned_dict[key] = value
        return returned_dict
