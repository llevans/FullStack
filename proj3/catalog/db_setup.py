#
# file: db_setup.py
# author: lyn.evans
# date: 09.07.15
#
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Era(Base):
    """ Classical musical eras model """
    __tablename__ = 'era'

    name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)

    @property
    def serialize(self):

        return {
            'name': self.name,
            'id': self.id,
        }


class Composer(Base):
    """  Composers model """
    __tablename__ = 'composer'

    name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(2000))
    # foreign key to eras table
    era_id = Column(Integer, ForeignKey('era.id'))
    era = relationship(Era)

    @property
    def serialize(self):

        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'era_id': self.era.id,
        }

# Initialize sqlalchmey database orm engine
engine = create_engine('postgresql://vagrant:vagrant@localhost:5432/vagrant')

Base.metadata.create_all(engine)
