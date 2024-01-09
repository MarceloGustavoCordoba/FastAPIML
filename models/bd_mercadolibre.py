# models.py
from sqlalchemy import Column, String, Integer, Boolean, ARRAY, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Notificacion(Base):
    __tablename__ = 'notificaciones'

    _id = Column(String(50), primary_key=True)
    topic = Column(String(255))
    resource = Column(String(255))
    user_id = Column(Integer)
    application_id = Column(Integer)
    sent = Column(TIMESTAMP(timezone=True))
    attempts = Column(Integer)
    received = Column(TIMESTAMP(timezone=True))
    actions = Column(ARRAY(String))
    revisado = Column(Boolean, default=False)
