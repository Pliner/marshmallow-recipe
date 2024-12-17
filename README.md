# marshmallow-recipe

The main goal of this opinionated library is to simplify migration from marshmallow2 to marshmallow3. 
Also, it helps with:
1. Stop writing marshmallow schemas completely: it generates them from dataclass. 
2. Using different naming cases(camel and capital camel cases are supported).
3. Utilizing best practises on fields configuration.

Supported types:
- `str`, `int`, `float`, `bool`, `datetime.datetime`, `datetime.date`, `datetime.time`, `decimal.Decimal`, `uuid.UUID`
- `Optional[T]`, `T | None`
- `Annotated`
- `list`, `dict` (with typed keys and values), `tuple` (only when all elements of the same type), `set`, `frozenset`
- `Mapping` (with typed keys and values), `Set`, `Sequence`

Example:

```python
import dataclasses
import datetime
import decimal
import marshmallow_recipe as mr
import uuid

from typing import Annotated

@dataclasses.dataclass(frozen=True)
class Transaction:
    id: uuid.UUID
    created_at: datetime.datetime
    processed_at: datetime.datetime | None
    amount: decimal.Decimal = dataclasses.field(metadata=mr.decimal_metadata(places=4))
    transaction_amount: Annotated[decimal.Decimal, mr.decimal_metadata(places=4)]

transaction = Transaction(
    id=uuid.uuid4(),
    created_at=datetime.datetime.utcnow(),
    processed_at=None,
    amount=decimal.Decimal(42),
    transaction_amount=decimal.Decimal(42),
 )

# dumps the transaction to a dict
raw = mr.dump(transaction) 

# loads a transaction from the dict
mr.load(Transaction, raw)

# provides a generated marshmallow schema for dataclass
mr.schema(Transaction)
```

Update API example:

```python
import decimal
import dataclasses
import marshmallow_recipe as mr

@dataclasses.dataclass(frozen=True)
@mr.options(none_value_handling=mr.NoneValueHandling.INCLUDE)
class CompanyUpdateData:
    name: str = mr.MISSING
    annual_turnover: decimal.Decimal | None = mr.MISSING

company_update_data = CompanyUpdateData(name="updated name")
dumped = mr.dump(company_update_data)
assert dumped == {"name": "updated name"}  # Note: no "annual_turnover" here

loaded = mr.load(CompanyUpdateData, {"name": "updated name"})
assert loaded.name == "updated name"
assert loaded.annual_turnover is mr.MISSING

loaded = mr.load(CompanyUpdateData, {"annual_turnover": None})
assert loaded.name is mr.MISSING
assert loaded.annual_turnover is None
```

Also generics are supported. All works automatically except one case. Dump operation of generic dataclass with `frozen=True` or `slots=True` requires explicitly specified subscripted generic type as `cls` argument of `dump` and `dump_many` methods.

```python
import dataclasses
from typing import Generic, TypeVar
import marshmallow_recipe as mr

T = TypeVar("T")

@dataclasses.dataclass()
class Regular(Generic[T]):
    value: T

mr.dump(Regular[int](value=123))  # it works without explicit cls arg

@dataclasses.dataclass(frozen=True)
class Frozen(Generic[T]):
    value: T

mr.dump(Frozen[int](value=123), cls=Frozen[int])  # cls required for frozen generic

@dataclasses.dataclass(slots=True)
class Slots(Generic[T]):
    value: T

mr.dump(Slots[int](value=123), cls=Slots[int])  # cls required for generic with slots

@dataclasses.dataclass(slots=True)
class SlotsNonGeneric(Slots[int]):
    pass

mr.dump(SlotsNonGeneric(value=123))  # cls not required

```
