from datetime import datetime
from typing import Annotated

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import mapped_column

int_pk = Annotated[
    int, mapped_column(primary_key=True, unique=True, autoincrement=True)
]
created_at = Annotated[
    datetime,
    mapped_column(
        type_=TIMESTAMP(timezone=True), server_default=func.now()
    )
]
updated_at = Annotated[
    datetime,
    mapped_column(
        type_=TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=datetime.now
    )
]
not_null_str = Annotated[
    str,
    mapped_column(nullable=True)
]
