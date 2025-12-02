from sqlalchemy import Column, Integer, Float, Text, Boolean, DateTime, JSON
from app.db.session import Base, SCHEMA_NAME


class PatientDDI(Base):
    """
    Model for existing patient_ddi_collapsed_from_topk table.
    Maps to existing RDS table WITHOUT creating/modifying it.
    
    IMPORTANT: 
    - This table has NO primary key in the original schema
    - Comorbidities uses JSON type (PostgreSQL: JSON/JSONB, SQLite: TEXT with auto serialization)
    - We use patient_uuid as primary_key for SQLAlchemy ORM requirements only
    """
    __tablename__ = "patient_ddi_collapsed_from_topk"
    
    # Tell SQLAlchemy this table already exists - DON'T create/modify it
    # Specify the schema conditionally (only for PostgreSQL, not SQLite)
    __table_args__ = {'schema': SCHEMA_NAME, 'extend_existing': True} if SCHEMA_NAME else {'extend_existing': True}
    
    # SQLAlchemy requires a primary key for ORM operations
    # Since the table doesn't have one, we'll use patient_uuid
    # This is ONLY for SQLAlchemy - not enforced in the database
    patient_uuid = Column(Text, primary_key=True, nullable=True)
    
    # All other columns matching exact schema from DDL
    drug1 = Column(Text, nullable=True)
    drug2 = Column(Text, nullable=True)
    drug1_norm = Column(Text, nullable=True)
    drug2_norm = Column(Text, nullable=True)
    overlap_start = Column(DateTime(timezone=True), nullable=True)
    overlap_stop = Column(DateTime(timezone=True), nullable=True)
    age = Column(Integer, nullable=True)
    sex = Column(Text, nullable=True)
    
    # Comorbidities stored as JSON (works with both PostgreSQL and SQLite)
    # PostgreSQL: native JSON/JSONB, SQLite: TEXT with automatic serialization
    comorbidities = Column(JSON, nullable=True)
    
    pair_key = Column(Text, nullable=True)
    unified_severity = Column(Text, nullable=True)
    unified_mechanism_text = Column(Text, nullable=True)
    ddi_confidence = Column(Float, nullable=True)  # DOUBLE PRECISION maps to Float
    ddi_known = Column(Boolean, nullable=True)
    
    def __repr__(self):
        return f"<PatientDDI(uuid={self.patient_uuid}, {self.drug1}+{self.drug2}, severity={self.unified_severity})>"
    
    class Config:
        orm_mode = True