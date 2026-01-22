from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repo = Column(String(200), unique=True, nullable=False)
    scanned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    issues_count = Column(Integer, default=0, nullable=False)


class Issue(Base):
    __tablename__ = "issues"

    pk = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    body = Column(Text, nullable=True)
    html_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, nullable=False)
    repo = Column(String(200), nullable=False)

    __table_args__ = (
        UniqueConstraint("id", "repo", name="uix_issue_repo"),
    )
