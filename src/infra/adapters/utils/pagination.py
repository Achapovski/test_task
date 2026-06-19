import base64
import json
from datetime import date, datetime
from typing import Any, Literal, Optional, Sequence, TypedDict, get_args, get_origin
from uuid import UUID

from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.interfaces import LoaderOption

from src.core.database.metadata import Base
from src.core.interfaces.models import AbstractDTO


async def get_keyset_page[Model: type[Base]](
    session: AsyncSession,
    model: Model,
    size: int,
    is_asc: bool,
    cursor_values: dict[str, Any],
    filter_queries: list[Any] = None,
    options: list[LoaderOption] = None,
    sort_fields: tuple = None,
) -> tuple[Sequence[Model], bool]:
    sort_fields = (model.id, model.created_at) if sort_fields is None else sort_fields

    stmt = select(model)
    stmt = stmt.options(*options) if options else stmt
    stmt = stmt.where(*filter_queries) if filter_queries else stmt

    last_values = [cursor_values.get(field.name) for field in sort_fields]

    if all(v is not None for v in last_values):
        current_values = tuple_(*sort_fields)  # type: ignore
        past_values = tuple_(*last_values)  # type: ignore
        stmt = stmt.where(current_values > past_values if is_asc else current_values < past_values)

    order_expr = (field.asc() if is_asc else field.desc() for field in sort_fields)
    stmt = stmt.order_by(*order_expr).limit(size + 1)

    result = (await session.scalars(stmt)).unique().all()
    return result[:size], len(result) > size


def parse_cursor(data: Optional[bytes], schema_cls: type[TypedDict]) -> dict[str, Any]:
    annotations = getattr(schema_cls, "__annotations__", {})
    cursor = dict.fromkeys(annotations)

    if not data:
        return cursor

    try:
        raw = json.loads(base64.urlsafe_b64decode(data).decode())
        cursor.update(raw)

        for key, annotation in annotations.items():
            value = cursor.get(key)
            if value is None:
                continue

            origin = get_origin(annotation)
            if origin in (Optional, Any, Literal) or origin is None:
                types = (annotation,)
            else:
                types = get_args(annotation)

            if datetime in types and isinstance(value, str):
                cursor[key] = datetime.fromisoformat(value)
            elif UUID in types and isinstance(value, str):
                cursor[key] = UUID(value)

    except (json.JSONDecodeError, ValueError, TypeError):
        return cursor
    return cursor


def build_cursor(
    items: Sequence[AbstractDTO], has_next: bool, fields: set[str], extra: dict[str, Any]
) -> Optional[bytes]:
    if not items or not has_next:
        return None
    last_item = items[-1]
    cursor_data = {}

    for key in fields:
        if not hasattr(last_item, key):
            continue

        value = getattr(last_item, key)
        if isinstance(value, (datetime, date)):
            value = value.isoformat()
        elif isinstance(value, UUID):
            value = str(value)

        cursor_data[key] = value

    cursor_data.update(extra)
    return base64.urlsafe_b64encode(json.dumps(cursor_data).encode())
