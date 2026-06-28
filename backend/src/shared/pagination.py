"""Optional, backward-compatible list pagination.

List endpoints accept ``?limit`` and ``?offset``. With no ``limit`` the full list
is returned (unchanged behaviour), so existing clients are unaffected; clients
that want pages pass the params. The response stays a flat array.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel


class PageParams(BaseModel):
    limit: int | None = None
    offset: int = 0


def _page_params(
    limit: Annotated[int | None, Query(ge=1, le=500)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PageParams:
    return PageParams(limit=limit, offset=offset)


PageDep = Annotated[PageParams, Depends(_page_params)]


def paginate[T](items: list[T], page: PageParams) -> list[T]:
    """Apply optional offset/limit; no limit returns everything from the offset."""
    if page.limit is None:
        return items[page.offset :]
    return items[page.offset : page.offset + page.limit]
