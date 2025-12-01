from sqlalchemy import Column, Text, Float
from app.db.session import Base, SCHEMA_NAME


class DDIRef(Base):
    """ Model for existing ddi_ref_unified table.
    Maps to existing RDS table WITHOUT creating/modifying it.
    
    IMPORTANT: 
    - This table has NO primary key in the original schema
    - sources_present is TEXT (JSON-like string), NOT a PostgreSQL ARRAY
    - We use pair_key as primary_key for SQLAlchemy ORM requirements only
    """
    __tablename__ = "ddi_ref_unified"

    # Tell SQLAlchemy this table already exists - DON'T create/modify it
    # Specify the schema conditionally (only for PostgreSQL, not SQLite)
    __table_args__ = {'schema': SCHEMA_NAME, 'extend_existing': True} if SCHEMA_NAME else {'extend_existing': True}

    # SQLAlchemy requires a primary key for ORM operations
    # Since the table doesn't have one, we'll use pair_key
    # This is ONLY for SQLAlchemy - not enforced in the database
    pair_key = Column(Text, nullable=True, primary_key=True)

    # All other columns matching exact schema from DDL
    drug1_norm = Column(Text, nullable=True)
    drug2_norm = Column(Text, nullable=True)
    unified_severity = Column(Text, nullable=True)
    unified_mechanism_text = Column(Text, nullable=True)
    sources_present = Column(Text, nullable=True)
    ddi_confidence = Column(Float, nullable=True)  # DOUBLE PRECISION maps to Float

    class Config:
        orm_mode = True