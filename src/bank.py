"""
This module contains the models used.
The syntax sticks to SQLAlchemy 1.4.

The two fundamental classes used are defined here:
- Account, with its 4 methods as features:
    - deposit,
    - withdraw,
    - transfer,
    - get_balance
- Transaction.
"""

from datetime import datetime
from typing import Union

from sqlalchemy import Column, Float, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


# Classes
class Account(Base):
    __tablename__ = "accounts"
    # Fields
    account_id = Column(Integer, primary_key=True)
    balance = Column(Float)
    # Relationships
    # One-to-Many: one account may have many transactions
    transactions = relationship("Transaction", back_populates="account")

    # Methods
    def __init__(self, session, account_id, balance: Union[float, int] = 0.0):
        """
        - account_id is, by default, automatically generated by SQLAlchemy (auto-incremented),
          but we will here initialize it with choosing it at instanciation.
        - the initial balance is obviously set to 0.
        """
        self.session = session
        self.account_id = account_id
        self.balance = balance

    def __repr__(self):
        return f"Account(id={self.account_id}, balance={self.balance:.2f})"

    # Should this be a class or static method?
    def is_valid_amount(self, amount) -> bool:
        """Convenience method to spot non-numerical or negative amounts."""
        try:
            amount = float(amount)
        except ValueError:
            return False
        if amount <= 0:
            return False
        return True

    def deposit(self, amount: Union[float, int]):
        if self.is_valid_amount(amount):
            self.balance += amount

            # Create this new deposit as a Transaction
            new_deposit = Transaction(
                account_id=self.account_id, amount=amount, type="deposit"
            )
            # Add this new deposit to `transactions` table and commit.
            self.session.add(new_deposit)
            self.session.commit()

    def withdraw(self, amount: Union[float, int]):
        if self.is_valid_amount(amount) and self.balance >= amount:
            self.balance -= amount

            # Create this new withdrawal as a Transaction
            new_withdrawal = Transaction(
                account_id=self.account_id, amount=amount, type="withdraw"
            )
            # Add this new withdrawal to `transactions` table and commit.
            self.session.add(new_withdrawal)
            self.session.commit()

    def transfer(self, other, amount: Union[float, int]):
        if self.is_valid_amount(amount) and self.balance >= amount:
            self.balance -= amount
            other.balance += amount
            # add change in `accounts` table
            # commit ?

            # Create these 2 new transactions
            new_withdrawal = Transaction(
                account_id=self.account_id, amount=amount, type="withdraw"
            )
            new_deposit = Transaction(
                account_id=other.account_id, amount=amount, type="deposit"
            )
            # add_all these 2 transactions in `transactions` table and commit.
            self.session.add_all([new_withdrawal, new_deposit])
            self.session.commit()

    def get_balance(self):
        return self.balance


class Transaction(Base):
    __tablename__ = "transactions"
    # Fields
    transaction_id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    amount = Column(Float)
    type = Column(String)
    timestamp = Column(DateTime)
    # Relationships
    # Many-to-One: any transaction has only one account
    account = relationship("Account", back_populates="transactions")

    # Methods
    def __init__(self, account_id, amount, type):
        self.account_id = account_id
        self.amount = amount
        self.type = type
        self.timestamp = datetime.now()
