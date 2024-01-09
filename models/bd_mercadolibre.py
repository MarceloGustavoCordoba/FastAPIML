# models.py
from sqlalchemy import Column, String, Integer, Boolean, ARRAY, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class Aplicacion(Base):
    __tablename__ = 'aplicaciones'

    site = Column(String(3), primary_key=True)
    app_id = Column(Integer, primary_key=True)
    client_secret = Column(String(255), nullable=False)
    uri = Column(String(255), nullable=False)
    callbacks = Column(String(255), nullable=False)

class ConexionCliente(Base):
    __tablename__ = 'conexion_clientes'

    app_id = Column(Integer, ForeignKey('aplicaciones.app_id'), nullable=False)
    code = Column(String(255), primary_key=True)
    access_token = Column(String(255), nullable=False)
    token_type = Column(String(255), nullable=False)
    expires_in = Column(Integer, nullable=False)
    scope = Column(String(255), nullable=False)
    user_id = Column(Integer, primary_key=True)
    refresh_token = Column(String(255), nullable=False)

    aplicacion = relationship('Aplicacion')

class Notificacion(Base):
    __tablename__ = 'notificaciones'

    _id = Column(String(50), primary_key=True)
    topic = Column(String(255))
    resource = Column(String(255))
    user_id = Column(Integer, ForeignKey('conexion_clientes.user_id'))
    application_id = Column(Integer, ForeignKey('aplicaciones.app_id'))
    sent = Column(TIMESTAMP(timezone=True))
    attempts = Column(Integer)
    received = Column(TIMESTAMP(timezone=True))
    actions = Column(ARRAY(String))
    revisado = Column(Boolean, default=False)

    aplicacion = relationship('Aplicacion')
    conexion_cliente = relationship('ConexionCliente')
