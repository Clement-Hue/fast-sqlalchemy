from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy import Integer, Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User

class AccountFactory(SQLAlchemyModelFactory):
    pass

class Other:
    pass