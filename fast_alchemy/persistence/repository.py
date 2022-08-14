from __future__ import annotations
import logging
from typing import TYPE_CHECKING, TypeVar, Generic
from abc import ABC

from sqlalchemy.orm import Query

if TYPE_CHECKING:
    from fast_alchemy.persistence.database import Database

logger = logging.getLogger(__name__)

T = TypeVar('T')

class EntityRepository(ABC, Generic[T]):
    entity: T = None
    not_found_exception = None

    def __init__(self, db: Database):
        self.db = db

    def _sorting(self, query: Query, sort_by: str =None) -> Query:
        """
        Sort an entity by its attributes pass as parameter

        :param sort_by: list of "attribute.(desc|asc)" pattern comma separated
        :return: query ordered
        """
        if sort_by is None: return query
        for sort in sort_by.split(","):
            try:
                attr_name, order = sort.split(".")
                attr = getattr(getattr(self._get_attribute_entity(attr_name), attr_name), order)
                query = query.order_by(attr())
            except (ValueError, AttributeError) as exc:
                logger.debug(f"Error during sorting: {exc}")
                continue
        return query

    def _get_attribute_entity(self, attr_name: str):
        """
        The entity to use when sorting

        :param attr_name: the attribute used to sort
        """
        return self.entity

    def get_all(self,sort_by=None, **filter) -> Query:
        query = self.db.session.query(self.entity).filter_by(**{
            k: v for k, v in filter.items() if v is not None
        })
        return self._sorting(query, sort_by)

    def get_by_pk(self, pk) -> T:
        entity = self.db.session.query(self.entity).get(pk)
        if not entity:
            raise self.not_found_exception()
        return entity
