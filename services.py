from sqlalchemy.orm import Session
from models import Issue, Scan
from typing import List, Dict
from datetime import datetime


def cache_issues(db: Session, repo: str, issues: List[Dict]) -> int:
    db.query(Issue).filter(Issue.repo == repo).delete()
    db.commit()

    for issue_data in issues:
        issue = Issue(**issue_data)
        db.add(issue)

    scan_record = db.query(Scan).filter(Scan.repo == repo).first()
    if scan_record:
        scan_record.scanned_at = datetime.utcnow()
        scan_record.issues_count = len(issues)
    else:
        scan_record = Scan(repo=repo, scanned_at=datetime.utcnow(), issues_count=len(issues))
        db.add(scan_record)

    db.commit()
    return len(issues)


def get_cached_issues(db: Session, repo: str) -> List[Issue]:
    return db.query(Issue).filter(Issue.repo == repo).all()


def is_repo_scanned(db: Session, repo: str) -> bool:
    return db.query(Scan).filter(Scan.repo == repo).first() is not None
