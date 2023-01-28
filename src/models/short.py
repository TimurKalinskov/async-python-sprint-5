from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from db.db import Base


class Short(Base):
    __tablename__ = 'url_shorts'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    url = Column(String(2048), unique=True, nullable=False)
    url_short = Column(String(256), unique=True, nullable=False)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    deleted = Column(Boolean, default=False, nullable=False, server_default='f')

    statistics = relationship('ShortStatistic')


class ShortStatistic(Base):
    __tablename__ = 'url_statistics'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    url_short = Column(ForeignKey('url_shorts.url_short', ondelete="CASCADE"), nullable=False)
    used_at = Column(DateTime, index=True, default=datetime.utcnow)
    client_host = Column(String(256), nullable=False)
    client_port = Column(Integer, nullable=False)

    author = relationship('Short', back_populates='statistics')
