import cProfile
import dataclasses
import datetime
import decimal
import marshmallow_recipe as mr
import uuid
import copy
import json

from typing import Annotated


def slow_dump(schema, obj):
    result = {}
    for field_name, field_schema in schema.items():
        name = field_schema["name"]
        optional = field_schema["optional"]
        type = field_schema["type"]
        field_value = getattr(obj, field_name)
        if field_value is None and optional:
            continue
        if not isinstance(field_value, type):
            raise Exception(f"Field {name} has invalid type {type(field_value)}")
        if isinstance(field_value, (datetime.datetime, datetime.date)):
            field_value = field_value.isoformat()
        elif isinstance(field_value, decimal.Decimal):
            if field_value.is_nan():
                raise Exception(f"Field {name} has invalid value {field_value}")
            field_value = str(field_value)
        elif isinstance(field_value, uuid.UUID):
            field_value = str(field_value)
        elif dataclasses.is_dataclass(field_value):
            field_value = slow_dump(field_schema["schema"], field_value)
        result[name] = field_value

    return result


@dataclasses.dataclass(frozen=True)
class Transaction:
    id: uuid.UUID
    created_at: datetime.datetime
    processed_at: datetime.datetime | None
    amount: decimal.Decimal = dataclasses.field(metadata=mr.decimal_metadata(places=4))
    transaction_amount: Annotated[decimal.Decimal, mr.decimal_metadata(places=4)]


transaction = Transaction(
    id=uuid.uuid4(),
    created_at=datetime.datetime.now(datetime.timezone.utc),
    processed_at=None,
    amount=decimal.Decimal(42),
    transaction_amount=decimal.Decimal(42),
)
transaction_schema = {
    # "id": {"name": "id", "type": str, "optional": False},
    "created_at": {"name": "created_at", "type": datetime.datetime, "optional": False},
    "processed_at": {"name": "processed_at", "type": datetime.datetime, "optional": True},
    "amount": {"name": "amount", "type": decimal.Decimal, "optional": False},
    "transaction_amount": {"name": "transaction_amount", "type": decimal.Decimal, "optional": False},
}
transactions = [copy.deepcopy(transaction) for i in range(100000)]

decimal.Decimal(0).is_nan()

# to warm up the lib caches
assert mr.load_many(Transaction, mr.dump_many(transactions))
assert mr.fast_dump(transaction_schema, transactions)
assert mr.fast_dump_bytes(transaction_schema, transactions)
assert [slow_dump(transaction_schema, t) for t in transactions]

cProfile.run("json.dumps(mr.dump_many(transactions)).encode('utf-8')", sort='tottime')
cProfile.run("json.dumps(mr.fast_dump(transaction_schema, transactions)).encode('utf-8')", sort='tottime')
cProfile.run("mr.fast_dump_bytes(transaction_schema, transactions)", sort='tottime')
cProfile.run("json.dumps([slow_dump(transaction_schema, t) for t in transactions]).encode('utf-8')", sort='tottime')
