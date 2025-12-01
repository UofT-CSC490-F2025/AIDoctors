#!/usr/bin/env python3
"""
Quick test to check if database has any DDI data.
Run: python quick_test_db.py
Set AWS credentials before running!
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Force production mode to use RDS
os.environ["ENVIRONMENT"] = "production"

from app.db.session import SessionLocal
from app.repositories.patientddi_repository import find_similar_interactions, get_interaction_statistics
from app.services.prediction_service import enrich_from_database
from app.schemas.db.prediction import DDIPredictRequest
from sqlalchemy import text

def quick_test():
    print("\n🔗 Connecting to RDS database...")
    db = SessionLocal()
    
    try:
        # Set schema to production
        db.execute(text("SET search_path TO production;"))
        
        print("\n" + "=" * 60)
        print("DATABASE QUICK TEST")
        print("=" * 60)
        
        # Test 1: Check if tables exist and have data
        print("\n1️⃣  Checking database tables...")
        try:
            result = db.execute(text("SELECT COUNT(*) FROM patient_ddi_collapsed_from_topk"))
            count = result.scalar()
            print(f"   ✅ patient_ddi_collapsed_from_topk table: {count} rows")
        except Exception as e:
            print(f"   ❌ Error accessing table: {e}")
            return
        
        # Test 2: Sample some drug pairs
        print("\n2️⃣  Sampling drug pairs from database...")
        try:
            result = db.execute(text("""
                SELECT DISTINCT drug1, drug2, COUNT(*) as count
                FROM patient_ddi_collapsed_from_topk
                GROUP BY drug1, drug2
                ORDER BY count DESC
                LIMIT 5
            """))
            print("   Top 5 drug pairs:")
            for row in result:
                print(f"     • {row[0]} + {row[1]}: {row[2]} cases")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
        
        # Test 2: Test enrich_from_database (complete RAG context)
        print("\n2️⃣  Testing enrich_from_database function (complete RAG context)...")
        try:
            # Create a prediction request with patient characteristics
            request = DDIPredictRequest(
                drug1="hydrochlorothiazide",
                drug2="lisinopril",
                Age=65,
                Sex="M",
            )
            
            print(f"   Request: {request.drug1} + {request.drug2}")
            print(f"   Patient: Age={request.Age}, Sex={request.Sex}, Comorbidities={request.Comorbidities}\n")
            
            # Get enriched context
            enriched = enrich_from_database(db, request)
            
            print(f"   📦 Enriched Context:")
            print(f"     • Similar cases found: {enriched.get('similar_cases_count', 0)}")
            print(f"     • Known interaction: {enriched.get('known_interaction', False)}")
            print(f"     • Average confidence: {enriched.get('avg_confidence', 0.0):.2f}")
            print(f"     • Static severity: {enriched.get('static_severity', 'Unknown')}")

            if enriched.get('severity_distribution'):
                print(f"     • Severity distribution:")
                for key, value in enriched['severity_distribution'].items():
                    print(f"       - {key}: {value}")
            
            mechanisms = enriched.get('mechanisms', [])
            print(f"\n     • Unique mechanisms found: {len(mechanisms)}")
            if mechanisms:
                print(f"       Top 3 mechanisms:")
                for i, mech in enumerate(mechanisms[:3], 1):
                    mech_display = mech[:60] + "..." if mech and len(mech) > 60 else (mech or "None")
                    print(f"         {i}. {mech_display}")
            
            rep_cases = enriched.get('representative_cases', [])
            print(f"\n     • Representative cases: {len(rep_cases)}")
            if rep_cases:
                print(f"       Top 3 most similar cases:")
                for i, case in enumerate(rep_cases[:3], 1):
                    similarity = case.get('similarity_score', 0)
                    # Format as percentage
                    similarity_pct = f"{similarity * 100:.1f}%"
                    print(f"\n         {i}. Patient: {case.get('patient_uuid', 'N/A')[:20]}... [Similarity: {similarity_pct}]")
                    print(f"            Age: {case.get('age')} | Sex: {case.get('sex')}")
                    print(f"            Severity: {case.get('severity')} | Confidence: {case.get('confidence')}")
                    comorbidities = case.get('comorbidities', 'None')
                    if isinstance(comorbidities, str):
                        comorbidities_display = comorbidities[:50] + "..." if len(comorbidities) > 50 else comorbidities
                    else:
                        comorbidities_display = str(comorbidities)[:50]
                    print(f"            Comorbidities: {comorbidities_display}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETE")
        print("=" * 60 + "\n")
        
    finally:
        db.close()

if __name__ == "__main__":
    quick_test()
