"""
Questions:
    Note: you should implement the Unit Tests in order to check that your code is working 

    1. Complete the `MiniVenmo.create_user()` method to allow our application to create new users.

    2. Complete the `User.pay()` method to allow users to pay each other. Consider the following: 
    if user A is paying user B, user's A balance should be used if there's enough balance to cover the whole payment, 
    if not, user's A credit card should be charged instead.

    3. Venmo has the Feed functionality, that shows the payments that users have been doing in the app.
    If Bobby paid Carol $5, and then Carol paid Bobby $15, it should look something like this
   

    Bobby paid Carol $5.00 for Coffee
    Carol paid Bobby $15.00 for Lunch

    Implement the `User.retrieve_feed()` and `MiniVenmo.render_feed()` methods so the MiniVenmo application can render the feed.

    4. Now users should be able to add friends. Implement the `User.add_friend()` method to allow users to add friends.
    5. Now modify the methods involved in rendering the feed to also show when user's added each other as friends.
"""

"""
MiniVenmo! Imagine that your phone and wallet are trying to have a beautiful
baby. In order to make this happen, you must write a social payment app.
Implement a program that will feature users, credit cards, and payment feeds.
"""

import re
import unittest
import uuid

users = {}

class UsernameException(Exception):
    pass


class PaymentException(Exception):
    pass


class CreditCardException(Exception):
    pass


class Payment:

    def __init__(self, amount, actor, target, note):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note
 

class User:

    def __init__(self, username):
        self.credit_card_number = None
        self.balance = 0.0
        self.friends:list[User] = []
        self.events = []

        if self._is_valid_username(username):
            self.username = username
        else:
            raise UsernameException('Username not valid.')


    def retrieve_feed(self):
        return self.events

    def add_friend(self, new_friend):
        self.friends.append(new_friend)
        new_friend.friends.append(self)
        self.events.append(f"{self.username} added {new_friend.username} as a friend.")
        new_friend.events.append(f"{new_friend.username} added {self.username} as a friend.")

    def add_to_balance(self, amount):
        self.balance += float(amount)

    def add_credit_card(self, credit_card_number):
        if self.credit_card_number is not None:
            raise CreditCardException('Only one credit card per user!')

        if self._is_valid_credit_card(credit_card_number):
            self.credit_card_number = credit_card_number

        else:
            raise CreditCardException('Invalid credit card number.')

    def pay(self, target, amount, note):
        amount = float(amount)
        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        elif self.credit_card_number is None:
            raise PaymentException('Must have a credit card to make a payment.')        
        if self.balance >= amount:
            payment = self.pay_with_balance(target, amount, note)
        else:
            payment = self.pay_with_card(target, amount, note)
        log = f"{self.username} paid {target.username} ${amount} for {note}"
        self.events.append(log)
        target.events.append(log)

    def pay_with_card(self, target, amount, note):
        amount = float(amount)

        self._charge_credit_card(self.credit_card_number)
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        return payment

    def pay_with_balance(self, target, amount, note):
        amount = float(amount)

        self.balance -= amount
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        return payment

    def _is_valid_credit_card(self, credit_card_number):
        return credit_card_number in ["4111111111111111", "4242424242424242"]

    def _is_valid_username(self, username):
        return re.match('^[A-Za-z0-9_\\-]{4,15}$', username)

    def _charge_credit_card(self, credit_card_number):
        # magic method that charges a credit card thru the card processor
        pass


class MiniVenmo:
    def create_user(self, username, balance, credit_card_number):
        user = User(username)
        user.balance = balance
        user.credit_card_number = credit_card_number

    def render_feed(self, feed):
        for event in feed:
            print(event)

    @classmethod
    def run(cls):
        venmo = cls()

        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        try:
            # should complete using balance
            bobby.pay(carol, 5.00, "Coffee")
 
            # should complete using card
            carol.pay(bobby, 15.00, "Lunch")
        except PaymentException as e:
            print(e)

        feed = bobby.retrieve_feed()
        venmo.render_feed(feed)

        bobby.add_friend(carol)


class TestUser(unittest.TestCase):

    def test_this_works(self):
        with self.assertRaises(UsernameException):
            raise UsernameException()

    def test_valid_username(self):
        user = User("Ricardo")
        self.assertEqual(user.username, "Ricardo")

    def test_invalid_username(self):
        with self.assertRaises(UsernameException):
            User("!#@!@#!")

    def test_valid_credit_card(self):
        user = User("Ricardo")
        user.add_credit_card("4111111111111111")
        self.assertEqual(user.credit_card_number, "4111111111111111")            

    def test_invalid_credit_card(self):
        user = User("Ricardo")
        with self.assertRaises(CreditCardException):
            user.add_credit_card("123")

    def test_add_friend(self):
        user1 = User("Ricardo")
        user2 = User("Peter")
        user1.add_friend(user2)
        self.assertIn(user2, user1.friends)
        self.assertIn(user1, user2.friends)

    def test_payment_with_card(self):
        user1 = User("Ricardo")
        user2 = User("Peter")
        user1.add_credit_card("4111111111111111")
        user1.pay(user2, 50.00, "Dinner")
        self.assertEqual(user2.balance, 50.00)

    def test_payment_with_balance(self):
        user1 = User("Ricardo")
        user2 = User("Peter")
        user1.add_credit_card("4111111111111111")
        user1.add_to_balance(50.00)
        user1.pay(user2, 20.00, "Lunch")
        self.assertEqual(user1.balance, 30.00)
        self.assertEqual(user2.balance, 20.00)

    def test_payment_self(self):
        user = User("Ricardo")
        with self.assertRaises(PaymentException):
            user.pay(user, 10.00, "Mistake")

    def test_payment_negative_amount(self):
        user1 = User("Ricardo")
        user2 = User("Peter")
        with self.assertRaises(PaymentException):
            user1.pay(user2, -5.00, "Invalid")

if __name__ == '__main__':
    unittest.main()