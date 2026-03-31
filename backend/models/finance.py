from pydantic import BaseModel  # TODO look more into validation


class DeltaIn(BaseModel):
    ts: str  # ISO date from frontend
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


class settingPin(BaseModel):
    id_t: int
    newPin: bool


class AddingAccount(BaseModel):
    ts: str  # ISO date from frontend
    name: str
    currency: str
    balance: float


class Archiving(BaseModel):
    id: int
    newArchivedState: bool
