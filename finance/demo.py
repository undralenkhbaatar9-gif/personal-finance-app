import hashlib
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from finance.counterparty import get_or_create_counterparty
from finance.db import get_session
from finance.models import Account, Bank, Budget, Category, Transaction
from finance.seed import seed

DEMO_ACCOUNT_NO = "DEMO-0001"


def _month_start(month_offset: int) -> date:
	today = date.today()
	month_index = today.year * 12 + today.month - 1 + month_offset
	return date(month_index // 12, month_index % 12 + 1, 1)


def load_demo_data(session: Session | None = None) -> int:
	"""Add six months of idempotent sample income and expenses; return rows added."""
	if session is None:
		with get_session() as active_session:
			return load_demo_data(active_session)

	seed(session)
	bank = session.scalar(select(Bank).where(Bank.code == "khan"))
	if bank is None:
		raise RuntimeError("Банкны суурь мэдээллийг ачаалж чадсангүй.")

	account = session.scalar(select(Account).where(Account.account_no == DEMO_ACCOUNT_NO))
	if account is None:
		account = Account(
			bank_id=bank.id,
			account_no=DEMO_ACCOUNT_NO,
			nickname="Туршилтын данс",
			currency="MNT",
			is_own=True,
		)
		session.add(account)
		session.flush()

	category_names = {
		("income", "Self-earned"),
		("expense", "Housing"),
		("expense", "Groceries"),
		("expense", "Utilities"),
		("expense", "Transportation"),
		("expense", "Restaurant"),
	}
	categories = {
		(category.kind, category.name): category
		for category in session.scalars(
			select(Category).where(
				Category.kind.in_([kind for kind, _ in category_names]),
				Category.name.in_([name for _, name in category_names]),
			)
		)
	}
	if len(categories) != len(category_names):
		raise RuntimeError("Туршилтын өгөгдөлд шаардлагатай ангиллууд олдсонгүй.")

	demo_budgets = {
		"Housing": Decimal("1000000.00"),
		"Groceries": Decimal("320000.00"),
		"Utilities": Decimal("160000.00"),
		"Transportation": Decimal("120000.00"),
		"Restaurant": Decimal("180000.00"),
	}
	existing_budget_ids = set(session.scalars(select(Budget.category_id)).all())
	for category_name, monthly_limit in demo_budgets.items():
		category = categories[("expense", category_name)]
		if category.id not in existing_budget_ids:
			session.add(Budget(category_id=category.id, monthly_limit=monthly_limit))

	existing_fingerprints = set(
		session.scalars(
			select(Transaction.fingerprint).where(Transaction.account_id == account.id)
		).all()
	)
	counterparties = {
		"salary": ("system:demo-salary", "Цалингийн орлого"),
		"housing": ("system:demo-housing", "Орон сууцны түрээс"),
		"groceries": ("system:demo-groceries", "Хүнсний дэлгүүр"),
		"utilities": ("system:demo-utilities", "Цахилгаан, дулаан"),
		"transport": ("system:demo-transport", "Тээврийн зардал"),
		"restaurant": ("system:demo-restaurant", "Кафе, ресторан"),
	}
	transactions: list[Transaction] = []
	balance = Decimal("2500000.00")
	for month_offset in range(-5, 1):
		first = _month_start(month_offset)
		days = [1, 3, 7, 10, 15, 19]
		if first.year == date.today().year and first.month == date.today().month:
			days = [min(day, max(1, date.today().day)) for day in days]
		rows = [
			("salary", "income", "Self-earned", Decimal("2800000.00"), "Цалин"),
			("housing", "expense", "Housing", Decimal("-900000.00"), "Орон сууцны түрээс"),
			("groceries", "expense", "Groceries", Decimal("-250000.00"), "Хүнсний худалдан авалт"),
			("utilities", "expense", "Utilities", Decimal("-120000.00"), "Цахилгаан, дулааны төлбөр"),
			("transport", "expense", "Transportation", Decimal("-75000.00"), "Тээврийн зардал"),
			("restaurant", "expense", "Restaurant", Decimal("-150000.00"), "Хоол, үйлчилгээ"),
		]
		for index, (cp_key, kind, category_name, amount, description) in enumerate(rows):
			txn_date = first.replace(day=days[index])
			counterparty_key, counterparty_name = counterparties[cp_key]
			counterparty = get_or_create_counterparty(
				session, counterparty_key, txn_date
			)
			counterparty.display_name = counterparty_name
			fingerprint_source = (
				f"demo-v1|{DEMO_ACCOUNT_NO}|{txn_date.isoformat()}|"
				f"{amount:.2f}|{category_name}"
			)
			fingerprint = hashlib.sha256(fingerprint_source.encode("utf-8")).hexdigest()
			if fingerprint in existing_fingerprints:
				continue
			balance_before = balance
			balance += amount
			transactions.append(
				Transaction(
					account_id=account.id,
					txn_datetime=datetime.combine(txn_date, datetime.min.time()).replace(hour=9 + index),
					amount=amount,
					balance_before=balance_before,
					balance_after=balance,
					description=description,
					counterparty_account=None,
					branch_code="DEMO",
					counterparty_id=counterparty.id,
					category_id=categories[(kind, category_name)].id,
					category_source="manual",
					fingerprint=fingerprint,
				)
			)
			existing_fingerprints.add(fingerprint)

	session.add_all(transactions)
	session.flush()
	return len(transactions)