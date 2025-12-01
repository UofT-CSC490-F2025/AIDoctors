from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.db.models.ddiref import DDIRef

def find_static_ddi_severity(
    db: Session,
    drug1: str,
    drug2: str
) -> Optional[str]:
    """
    Look up the static DDI reference table for known severity of a drug pair.
    Returns the severity string if found, else None.
    """
    condition = or_(
        and_(
            func.lower(DDIRef.drug1_norm) == func.lower(drug1),
            func.lower(DDIRef.drug2_norm) == func.lower(drug2)
        ),
        and_(
            func.lower(DDIRef.drug1_norm) == func.lower(drug2),
            func.lower(DDIRef.drug2_norm) == func.lower(drug1)
        )
    )
    result = db.query(DDIRef.unified_severity).filter(condition).first()
    if result and result.unified_severity:
        return result.unified_severity
    return None