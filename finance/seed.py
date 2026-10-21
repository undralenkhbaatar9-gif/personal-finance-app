from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from finance.db import get_session
from finance.models import Bank, Category, Rule

SEED_FILE = Path(__file__).resolve().parent.parent / "seed" / "categories.yaml"


def _load_seed_data() -> dict[str, Any]:
    with SEED_FILE.open(encoding="utf-8") as seed_file:
        data = yaml.safe_load(seed_file)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid seed data in {SEED_FILE}")
    return data


def _seed(session: Session, data: dict[str, Any]) -> None:
    for bank_data in data["banks"]:
        bank = session.scalar(select(Bank).where(Bank.code == bank_data["code"]))
        if bank is None:
            session.add(Bank(code=bank_data["code"], name=bank_data["name"]))
        else:
            bank.name = bank_data["name"]

    session.flush()

    categories = data["categories"]
    for kind in ("income", "expense"):
        for name in categories[kind]:
            category = session.scalar(
                select(Category).where(Category.kind == kind, Category.name == name)
            )
            if category is None:
                session.add(Category(kind=kind, name=name, in_reports=True))

    transfer_data = categories["transfer"]
    for name in transfer_data["names"]:
        category = session.scalar(
            select(Category).where(Category.kind == "transfer", Category.name == name)
        )
        if category is None:
            session.add(
                Category(
                    kind="transfer",
                    name=name,
                    in_reports=transfer_data["in_reports"],
                )
            )

    session.flush()

    for rule_data in data["rules"]:
        category = session.scalar(
            select(Category).where(
                Category.kind == rule_data["category_kind"],
                Category.name == rule_data["category_name"],
            )
        )
        if category is None:
            raise ValueError(
                f"Seed category not found: {rule_data['category_kind']}: "
                f"{rule_data['category_name']}"
            )
        existing_rule = session.scalar(
            select(Rule).where(
                Rule.priority == rule_data["priority"],
                Rule.field == rule_data["field"],
                Rule.match_type == rule_data["match_type"],
                Rule.pattern == rule_data["pattern"],
                Rule.amount_sign == rule_data["amount_sign"],
                Rule.category_id == category.id,
            )
        )
        if existing_rule is None:
            session.add(
                Rule(
                    priority=rule_data["priority"],
                    field=rule_data["field"],
                    match_type=rule_data["match_type"],
                    pattern=rule_data["pattern"],
                    amount_sign=rule_data["amount_sign"],
                    category_id=category.id,
                    active=True,
                )
            )


def seed(session: Session | None = None) -> None:
    """Insert or update the banks, categories, and rules from the seed file."""
    data = _load_seed_data()
    if session is not None:
        _seed(session, data)
        return

    with get_session() as active_session:
        _seed(active_session, data)


if __name__ == "__main__":
    seed()