import cProfile
import dataclasses
import datetime
import decimal
import uuid

import marshmallow_recipe as mr


@dataclasses.dataclass(frozen=True)
class Transaction:
    id: uuid.UUID
    created_at: datetime.datetime
    processed_at: datetime.datetime | None
    amount: decimal.Decimal
    transaction_amount: decimal.Decimal


transaction = Transaction(
    id=uuid.uuid4(),
    created_at=datetime.datetime.now(datetime.timezone.utc),
    processed_at=None,
    amount=decimal.Decimal(42),
    transaction_amount=decimal.Decimal(42),
 )


assert mr.load_many(Transaction, mr.dump_many([transaction] * 128))
assert mr.load_slim_many(Transaction, mr.dump_slim_many([transaction] * 128))
cProfile.run("mr.load_slim_many(Transaction, mr.dump_slim_many([transaction] * 128))", sort='tottime')
cProfile.run("mr.load_many(Transaction, mr.dump_many([transaction] * 128))", sort='tottime')
