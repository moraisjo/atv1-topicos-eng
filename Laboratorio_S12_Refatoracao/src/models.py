from dataclasses import dataclass


@dataclass(frozen=True)
class Customer:
    name: str
    plan: str = "REGULAR"


@dataclass(frozen=True)
class Item:
    name: str
    price: float
    qty: int = 1


@dataclass(frozen=True)
class Order:
    customer: Customer
    items: tuple[Item, ...]
