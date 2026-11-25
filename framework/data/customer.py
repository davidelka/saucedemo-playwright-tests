"""The customer details used at checkout."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Customer:
    first_name: str
    last_name: str
    postal_code: str


CUSTOMER = Customer("John", "Doe", "12345")
