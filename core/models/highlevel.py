from typing import Optional
import datetime

from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
	pass


class GoHighLevelMessage(Base):
	__tablename__ = 'GoHighLevelMessage'

	id: Mapped[str] = mapped_column(mysql.CHAR(20, collation='utf8mb4_unicode_ci'), primary_key=True)
	type: Mapped[int] = mapped_column(Integer, nullable=False)
	messageType: Mapped[str] = mapped_column(String(50, collation='utf8mb4_unicode_ci'), nullable=False)
	locationId: Mapped[str] = mapped_column(mysql.CHAR(20, collation='utf8mb4_unicode_ci'), nullable=False)
	contactId: Mapped[str] = mapped_column(mysql.CHAR(20, collation='utf8mb4_unicode_ci'), nullable=False)
	conversationId: Mapped[str] = mapped_column(mysql.CHAR(20, collation='utf8mb4_unicode_ci'), nullable=False)
	dateAdded: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
	attachments: Mapped[dict] = mapped_column(JSON, nullable=False)
	createdAt: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
	updatedAt: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
	body: Mapped[Optional[str]] = mapped_column(mysql.LONGTEXT(collation='utf8mb4_unicode_ci'), nullable=True)
	direction: Mapped[Optional[str]] = mapped_column(String(30, collation='utf8mb4_unicode_ci'), nullable=True)
	status: Mapped[Optional[str]] = mapped_column(String(30, collation='utf8mb4_unicode_ci'), nullable=True)
	contentType: Mapped[Optional[str]] = mapped_column(String(100, collation='utf8mb4_unicode_ci'), nullable=True)
	meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
	source: Mapped[Optional[str]] = mapped_column(String(100, collation='utf8mb4_unicode_ci'), nullable=True)
	userId: Mapped[Optional[str]] = mapped_column(String(20, collation='utf8mb4_unicode_ci'), nullable=True)
	conversationProviderId: Mapped[Optional[str]] = mapped_column(String(20, collation='utf8mb4_unicode_ci'), nullable=True)


class IsrLeadTouchpoint(Base):
	__tablename__ = 'isrLeadTouchpoint'

	dateAdded: Mapped[datetime.datetime] = mapped_column(DateTime, primary_key=True)
	locationId: Mapped[str] = mapped_column(mysql.CHAR(20), primary_key=True)
	contactId: Mapped[str] = mapped_column(mysql.CHAR(20), primary_key=True)
	type: Mapped[str] = mapped_column(String(255), primary_key=True)
	direction: Mapped[str] = mapped_column(String(255), nullable=False)
	context: Mapped[str] = mapped_column(mysql.MEDIUMTEXT(), primary_key=True)
