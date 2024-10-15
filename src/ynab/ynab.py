from typing import Any, TypeVar, Generic, Literal
from abc import ABC, abstractmethod
import requests
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# TODO: figure out fetch methods
# TODO: preferably without parent refrence

__all__ = ["Model", "Group", "YNAB", "Budget", "Account"]

class Model(BaseModel, ABC):
    id: str
    name: str

    @abstractmethod
    def fetch(self, attr: str) -> Any: pass

    def update(self, data: dict[str, Any]) -> None:
        new_data = self.model_dump()
        new_data.update(data)
        self.__dict__ = self.__class__(**new_data).__dict__

    def __getattribute__(self, name: str) -> Any:
        r = super().__getattribute__(name)
        if r is None:
            if name in self.model_fields.keys():
                return self.fetch(name)
        return r


T = TypeVar("T", "Budget", "Account")
class Group(BaseModel, Generic[T]):
    contents: list[T]
    
    @property
    def id_dict(self) -> dict[str, T]:
        return {c.id: c for c in self.contents}
    @property
    def name_dict(self) -> dict[str, T]:
        return {c.name: c for c in self.contents}
    
    def __getitem__(self, value: str|int) -> Any:
        if isinstance(value, int):
            return self.contents[value]
        else:
            if value in self.id_dict.keys():
                return self.id_dict[value]
            elif value in self.name_dict.keys():
                return self.name_dict[value]
            
        raise KeyError(f"`{value}` is an invalid lookup, not an index (int), id (str), or name (str)")



class Account(Model):
    type: Literal["checking"] | None = None

    on_budget: bool | None = None
    closed: bool | None = None
    note: str | None = None
    balance: float | None = None
    cleared_balance: float | None = None
    uncleared_balance: float | None = None

    transfer_payee_id: str | None = None

    deleted: bool | None = None

    def fetch(self, attr: str) -> Any:
        data = requests.get(f"https://api.ynab.com/v1/budgets/{id}/accounts/{self.id}").json()["data"]["budget"]
        self.update(data)
        return getattr(self, attr)


class Currency(BaseModel):
    iso_code: str
    example_format: str
    decimal_digits: int
    descimal_separator: str
    symbol_first: bool
    group_separator: str
    currency_symbol: str
    display_symbol: bool

class Budget(Model):

    last_modified_on: datetime | None = None
    first_month: datetime | None = None
    last_month: datetime | None = None
    date_format: dict[str, str] | None = None

    currency_format: Currency | None = None

    accounts: Group[Account] | None = None


    def fetch(self, attr: str) -> Any:
        data = requests.get(f"https://api.ynab.com/v1/budgets/{self.id}").json()["data"]["budget"]
        self.update(data)
        return getattr(self, attr)


class YNAB:
    BASE = "https://api.ynab.com/v1/"
    def __init__(self, token: str) -> None:
        self.token = token
        self.budgets: Group[Budget]

    def get(self, path: str) -> None:
        requests.get(self.BASE+path).json()["data"]

