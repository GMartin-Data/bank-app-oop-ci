from src.bank import Transaction  # Used within queries on Mock objects


def test_deposit_normal(account_factory, my_session):
    """Simple test with positive amount"""
    with my_session:
        account = account_factory(account_id=1, balance=100)
        account.deposit(50)
        # Checks
        # 1. Verify that current balance is updated
        assert account.balance == 150
        # 2. Verify a new transaction has been correctly added with 'deposit' type
        assert my_session.query(Transaction).count() == 1
        assert (
            my_session.query(Transaction)
            .filter(Transaction.transaction_id == 1)  # Maybe too picky and not needed
            .one()
        ).type == "deposit"
        # 3. Verify the new transaction's timestamp has been correctly added
        assert (
            my_session.query(Transaction)
            .filter(Transaction.transaction_id == 1)  # Maybe too picky and not needed
            .one()
        ).timestamp
        # 4. Verify session.commit has been called.
        assert my_session.commit.call_count == 2
        # my_session.commit.assert_any_call()
        # The non-commented is better as `session.commit` is also called within account_factory


def test_deposit_negative_amount(account_factory, my_session):
    with my_session:
        account = account_factory(account_id=1, balance=100)
        account.deposit(-50)
        # Checks
        # 1. Verify the account balance remains unchanged
        assert account.balance == 100
        # 2. Verify no transaction was created
        assert my_session.query(Transaction).count() == 0
        # 3. Verify that session.commit wasn't called
        assert my_session.commit.call_count == 1


def test_deposit_zero_amount(account_factory, my_session):
    with my_session:
        account = account_factory(account_id=1, balance=100)
        account.deposit(0)
        # Checks
        # 1. Verify the account balance remains unchanged
        assert account.balance == 100
        # 2. Verify no transaction was created
        assert my_session.query(Transaction).count() == 0
        # 3. Verify that session.commit wasn't called
        assert my_session.commit.call_count == 1


def test_withdraw_normal(account_factory, my_session):
    with my_session:
        account = account_factory(account_id=1, balance=100)
        account.withdraw(30)
        # Checks
        # 1. Verify the account balance is correctly updated
        assert account.balance == 70
        # 2. Verify a new transaction has been correctly added with 'withdraw' type
        assert my_session.query(Transaction).count() == 1
        assert (
            my_session.query(Transaction)
            .filter(Transaction.transaction_id == 1)  # Maybe too picky and not needed
            .one()
        ).type == "withdraw"
        # 4. Verify session.commit has been called.
        assert my_session.commit.call_count == 2


def test_withdraw_insufficient_funds(account_factory, my_session):
    with my_session:
        account = account_factory(account_id=1, balance=100)
        account.withdraw(200)
        # Checks
        # 1. Verify the account balance remains unchanged
        assert account.balance == 100
        # 2. Verify no transaction was created
        assert my_session.query(Transaction).count() == 0
        # 3. Verify that session.commit wasn't called
        assert my_session.commit.call_count == 1


def test_withdraw_negative_amount(account_factory, my_session):
    with my_session:
        account = account_factory(account_id=1, balance=100)
        account.withdraw(-300)
        # Checks
        # 1. Verify the account balance remains unchanged
        assert account.balance == 100
        # 2. Verify no transaction was created
        assert my_session.query(Transaction).count() == 0
        # 3. Verify that session.commit wasn't called
        assert my_session.commit.call_count == 1


def test_withdraw_zero_amount(account_factory, my_session):
    with my_session:
        account = account_factory(account_id=1, balance=100)
        account.withdraw(0)
        # Checks
        # 1. Verify the account balance remains unchanged
        assert account.balance == 100
        # 2. Verify no transaction was created
        assert my_session.query(Transaction).count() == 0
        # 3. Verify that session.commit wasn't called
        assert my_session.commit.call_count == 1


def test_transfer_normal(account_factory, my_session):
    with my_session:
        account1 = account_factory(account_id=1, balance=100)
        account2 = account_factory(account_id=1, balance=50)
        account1.transfer(account2, 20)
        # Checks
        # 1. Verify the amount is deduced from the source account's balance
        assert account1.balance == 80
        # 2. Verify the amount is added to the destination account's balance
        assert account2.balance == 70
        # 3. Verify two transactions are created with the appropriate types
        assert my_session.query(Transaction).count() == 2
        results = my_session.query(Transaction).all()
        # WARNING: There's a weird error when
        # filtering by transaction_id and using .one()
        assert results[0].type == "withdraw" and results[1].type == "deposit"
        # 4. Verify session.commit has been called
        assert (
            my_session.commit.call_count == 3
        )  # 2 for accounts, 1 for both transactions


def test_transfer_insufficient_funds(account_factory, my_session):
    with my_session:
        account1 = account_factory(account_id=1, balance=100)
        account2 = account_factory(account_id=2, balance=50)
        account1.transfer(account2, 200)
        # Checks
        # 1. Verify both accounts' balance remain unchanged
        assert account1.balance == 100 and account2.balance == 50
        # 2. Verify no transaction was added
        assert my_session.query(Transaction).count() == 0
        # 3. Verify that session.commit wasn't called
        assert my_session.commit.call_count == 2  # One for each account


def test_transfer_negative_amount(account_factory, my_session):
    with my_session:
        account1 = account_factory(account_id=1, balance=100)
        account2 = account_factory(account_id=2, balance=50)
        account1.transfer(account2, -200)
        # Checks
        # 1. Verify both accounts' balance remain unchanged
        assert account1.balance == 100 and account2.balance == 50
        # 2. Verify no transaction was added
        assert my_session.query(Transaction).count() == 0
        # 3. Verify that session.commit wasn't called
        assert my_session.commit.call_count == 2  # One for each account


def test_transfer_zero_amount(account_factory, my_session):
    with my_session:
        account1 = account_factory(account_id=1, balance=100)
        account2 = account_factory(account_id=2, balance=50)
        account1.transfer(account2, 0)
        # Checks
        # 1. Verify both accounts' balance remain unchanged
        assert account1.balance == 100 and account2.balance == 50
        # 2. Verify no transaction was added
        assert my_session.query(Transaction).count() == 0
        # 3. Verify that session.commit wasn't called
        assert my_session.commit.call_count == 2  # One for each account


def test_get_balance_initial(account_factory, my_session):
    with my_session:
        account1 = account_factory(
            account_id=1,
        )
        account2 = account_factory(account_id=2, balance=100)
        # 1. Verify the initial balance whenever a new account is created
        assert account1.get_balance() == 0
        # 2. Verify the initial balance is correct for an account
        #    created with an specified initial balance
        assert account2.get_balance() == 100
        # 3. Verify there are no transactions
        assert my_session.query(Transaction).count() == 0


def test_get_balance_after_deposit(account_factory, my_session):
    with my_session:
        account = account_factory(account_id=1, balance=200)
        account.deposit(500)
        # 1. Check if the new balance includes the deposit's amount
        assert account.get_balance() == 700


def test_get_balance_after_withdrawal(account_factory, my_session):
    with my_session:
        account = account_factory(account_id=1, balance=400)
        account.withdraw(150)
        # 1. Check if the new balance includes the deposit's amount
        assert account.get_balance() == 250


def test_get_balance_after_failed_withdrawal(account_factory, my_session):
    with my_session:
        account = account_factory(account_id=1, balance=400)
        account.withdraw(500)
        # 1. Check if the new balance includes the deposit's amount
        assert account.get_balance() == 400


def test_get_balance_after_transfer(account_factory, my_session):
    with my_session:
        account1 = account_factory(account_id=1, balance=400)
        account2 = account_factory(account_id=2, balance=100)
        account1.transfer(account2, 250)
        # 1. Check that the two accounts' balances have been correctly modified
        assert account1.balance == 150
        assert account2.balance == 350
