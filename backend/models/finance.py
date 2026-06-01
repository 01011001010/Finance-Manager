from pydantic import BaseModel, field_validator
from re import search, fullmatch
from pydantic_extra_types.currency_code import ISO4217
from datetime import datetime
# TODO implement more validation


class DeltaIn(BaseModel):
    ts: datetime  # ISO date from frontend
    subtitle: str | None = None
    amount: float
    id_a: int
    tag: int | None = None


class TransactionWithDelta(BaseModel):
    title: str
    delta: DeltaIn


class AddingDelta(BaseModel):
    id_t: int
    delta: DeltaIn


class AddingTag(BaseModel):
    tag_name: str
    parent: int | None = None

    @field_validator("tag_name")
    @classmethod
    def validate_tag_name(cls, value: str) -> str:
        value = value.strip()

        # Blank tag
        if not value:
            raise ValueError("Tag cannot be blank")

        # Explicit ban of / and \
        if search(r"[/\\]", value):
            raise ValueError("'/' and '\\' are reserved and cannot be part of a tag")

        # General check for allowed characters
        if not fullmatch(r"^[a-zA-Z0-9\s.,&\-]+$", value):
            raise ValueError("Only letters, numbers, spaces, and [ , . & - ] are "
                             "allowed")

        return value


class settingPin(BaseModel):
    id_t: int
    newPin: bool


class AddingAccount(BaseModel):
    ts: datetime  # ISO date from frontend
    name: str
    currency: ISO4217
    balance: float

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        # TODO more complex check in desired
        value = value.strip()
        if not value:
            raise ValueError("Account name is required and cannot be blank")
        return value


class Archiving(BaseModel):
    id: int
    newArchivedState: bool
