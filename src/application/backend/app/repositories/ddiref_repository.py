from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, select, union, func

from app.db.models.ddiref import DDIRef


def find_static_ddi_severity(db: Session, drug1: str, drug2: str) -> Optional[str]:
    """
    Look up the static DDI reference table for known severity of a drug pair.
    Returns the severity string if found, else None.
    """
    condition = or_(
        and_(
            func.lower(DDIRef.drug1_norm) == func.lower(drug1),
            func.lower(DDIRef.drug2_norm) == func.lower(drug2),
        ),
        and_(
            func.lower(DDIRef.drug1_norm) == func.lower(drug2),
            func.lower(DDIRef.drug2_norm) == func.lower(drug1),
        ),
    )
    result = db.query(DDIRef.unified_severity).filter(condition).first()
    if result and result.unified_severity:
        return result.unified_severity
    return None


def search_matching_drug_names(db: Session, drug_name: str, limit: int) -> List[str]:
    """
    Searches for unique drug names in DDIRef matching the input string.
    Returns the top `limit` closest matches (shortest strings first) for a dropdown.
    """
    if not drug_name:
        return []

    search_pattern = f"%{drug_name}%"
    d1 = select(DDIRef.drug1_norm.label("name")).where(
        DDIRef.drug1_norm.ilike(search_pattern)
    )
    d2 = select(DDIRef.drug2_norm.label("name")).where(
        DDIRef.drug2_norm.ilike(search_pattern)
    )
    union_stmt = union(d1, d2).subquery().alias("union_result")
    final_stmt = (
        select(union_stmt.c.name).order_by(func.length(union_stmt.c.name)).limit(limit)
    )
    results = db.execute(final_stmt).scalars().all()

    return results
