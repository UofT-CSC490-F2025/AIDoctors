from sqlalchemy import Column, Integer, Float, Text, Boolean, DateTime, ARRAY
from app.db.session import Base, SCHEMA_NAME


class PatientDDI(Base):
    """
    Model for existing patient_ddi_collapsed_from_topk table.
    Maps to existing RDS table WITHOUT creating/modifying it.
    
    IMPORTANT: 
    - This table has NO primary key in the original schema
    - Comorbidities is TEXT (JSON-like string), NOT a PostgreSQL ARRAY
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
    
    # Comorbidities is now a PostgreSQL ARRAY of TEXT
    comorbidities = Column(ARRAY(Text), nullable=True)
    
    pair_key = Column(Text, nullable=True)
    unified_severity = Column(Text, nullable=True)
    unified_mechanism_text = Column(Text, nullable=True)
    ddi_confidence = Column(Float, nullable=True)  # DOUBLE PRECISION maps to Float
    ddi_known = Column(Boolean, nullable=True)
    
    def __repr__(self):
        return f"<PatientDDI(uuid={self.patient_uuid}, {self.drug1}+{self.drug2}, severity={self.unified_severity})>"
    
    @property
    def comorbidities_list(self):
        """
        Parse Comorbidities from TEXT to list.
        The loader stores it as a string representation of a Python list.
        Example: "['Hypertension', 'Diabetes']"
        """
        if not self.Comorbidities:
            return []
        
        import json
        import ast
        
        comorbidities_str = self.Comorbidities.strip()
        
        # Handle empty strings or "[]"
        if not comorbidities_str or comorbidities_str == "[]":
            return []
        
        # Try JSON parsing first (if it's valid JSON)
        if comorbidities_str.startswith('['):
            try:
                return json.loads(comorbidities_str)
            except json.JSONDecodeError:
                pass
        
        # Try Python literal eval (most common from your pipeline)
        try:
            result = ast.literal_eval(comorbidities_str)
            if isinstance(result, list):
                return [str(item) for item in result]  # Ensure all items are strings
        except (ValueError, SyntaxError):
            pass
        
        # Fallback: split by comma (if it's a comma-separated string)
        if ',' in comorbidities_str:
            return [c.strip() for c in comorbidities_str.split(',') if c.strip()]
        
        # Last resort: return as single-item list
        return [comorbidities_str]
    
    class Config:
        orm_mode = True