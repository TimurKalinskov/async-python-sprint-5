from datetime import datetime
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, ForeignKey,
    UniqueConstraint, func, FetchedValue
)

from db.db import Base


class File(Base):
    __tablename__ = 'files'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(256), nullable=False)
    created_at = Column(
        DateTime, index=True, default=func.now(), onupdate=func.now(),
        server_default=func.now(), server_onupdate=func.now()
    )
    path = Column(Text, unique=True, nullable=False)
    size = Column(Integer, nullable=False, default=0)
    is_downloadable = Column(Boolean, default=True, nullable=False)
    account_id = Column(
        ForeignKey('users.id', ondelete='SET NULL'), nullable=True
    )
    content_type = Column(String(256), nullable=True)
    extension = Column(String(256), nullable=True)

    account = relationship('User', back_populates='files')
    path_uniq_constraint = UniqueConstraint(path, name='path_uniq')
