import pytest

from fast_alchemy.persistence.database import Database
from fast_alchemy.persistence.repository import EntityRepository
from sqlalchemy import Integer, Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class UserNotFound(Exception):
    pass

class UserRepository(EntityRepository[User]):
    entity = User
    not_found_exception = UserNotFound


@pytest.fixture()
def db():
    db= Database("sqlite://", repositories=[UserRepository])
    Base.metadata.create_all(db.engine)
    return db

def test_get_by_pk(db):
    user = User(id=1, name="Paul")
    with db.session_ctx():
        db.session.add(user)
        db.session.commit()
        user_repo = db.get_repository(UserRepository)
        assert isinstance(user_repo.get_by_pk(1), User)

def test_get_by_pk_not_found(db):
    with db.session_ctx():
        user_repo = db.get_repository(UserRepository)
        with pytest.raises(UserNotFound):
            user = user_repo.get_by_pk(1)

def test_get_all(db):
    with db.session_ctx():
        users = [User(id=1, name="Paul"), User(id=2, name="Pierre")]
        db.session.add_all(users)
        db.session.commit()
        user_repo = db.get_repository(UserRepository)
        assert user_repo.get_all().all() == users

def test_get_all_filtered(db):
    with db.session_ctx():
        users = [User(id=1, name="Paul"), User(id=2, name="Pierre")]
        db.session.add_all(users)
        db.session.commit()
        user_repo = db.get_repository(UserRepository)
        assert user_repo.get_all(name="Paul").all() == [users[0]]

def test_get_all_sorting(db):
    with db.session_ctx():
        users = [User(id=1, name="Paul"), User(id=2, name="Anne")]
        db.session.add_all(users)
        db.session.commit()
        user_repo = db.get_repository(UserRepository)
        assert user_repo.get_all(sort_by="name.asc").all() == [users[1], users[0]]
