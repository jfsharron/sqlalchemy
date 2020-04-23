from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

# Base
Base = declarative_base() 

# Concrete type
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return "<User(id: %r, name: %r)>" % (self.id, self.name)

# Engine and create tables
from sqlalchemy import create_engine
engine = create_engine("sqlite://", echo=True)
Base.metadata.create_all(engine)

# Session with identity map
from sqlalchemy.orm import Session
session = Session(bind=engine)

# adding multiple objects as *pending*
u1 = User(name="slavo")
session.add_all([
    u1,
    User(name="jano"),
    User(name="vlado"),
    User(name="peter"),
    User(name="brano")
])

# finalize transaction
session.commit();

# Many-to-One relationship (Adr->User - one user can live on multiple addresses)
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# in sqlalchemy we have to declare relation ship twice
# 1) relation type at core level
# 2) relationship on orm level and object level
class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))

    user = relationship("User", backref="addresses") # creates addresses property on referenced object

    def __repr__(self):
        return "<Address(%r)>" % self.email

# Creates addresses table
Base.metadata.create_all(engine)

u1 = User(name="Matus")

u1.addresses = [
    Address(email="matus@matus.com"),
    Address(email="matus@woho.com"),
    Address(email="matus@microsoft.io")
]

session.add(u1) # also added addresses
session.commit()

# -----------------------------------------------------------
# Aliases
# -----------------------------------------------------------

# query that refers to the same entity more than once in the FROM clause requires *aliasing*

from sqlalchemy.orm import aliased

a1, a2 = aliased(Address), aliased(Address)

rows = session.query(User).\
    join(a1).\
    join(a2).\
    filter(a1.email == "matus@woho.com").\
    filter(a2.email == "matus@microsoft.io").\
    all()

for row in rows:
    print(row)

# from ORM to CORE
q = session.query(User) # orm query
subq = q.subquery()     # core query

print("------------")
print(q)
print(subq)
print(subq.element)
print(subq.element.froms)
