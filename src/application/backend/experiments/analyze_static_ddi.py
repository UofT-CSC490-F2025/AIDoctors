#!/usr/bin/env python3
"""
Analyze static DDI reference data and compare with patient case counts.
Shows drug pairs with known severity from static tables, ranked by patient cases.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Force production mode to use RDS
os.environ["ENVIRONMENT"] = "production"

from app.db.session import SessionLocal
from sqlalchemy import text
import pandas as pd

def analyze_static_ddi():
    print("\n🔗 Connecting to RDS database...")
    db = SessionLocal()
    
    try:
        # Set schema to production
        db.execute(text("SET search_path TO production;"))
        
        print("\n" + "=" * 80)
        print("STATIC DDI ANALYSIS")
        print("=" * 80)
        
        # Query: Get static DDI pairs with severity and count patient cases
        print("\n📊 Fetching DDI pairs with static severity and patient case counts...")
        
        query = text("""
            WITH static_ddi AS (
                SELECT 
                    pair_key,
                    drug1_norm,
                    drug2_norm,
                    unified_severity,
                    unified_mechanism_text,
                    ddi_confidence
                FROM ddi_ref_unified
                WHERE unified_severity IS NOT NULL
            ),
            patient_counts AS (
                SELECT 
                    pair_key,
                    COUNT(*) as patient_case_count,
                    COUNT(DISTINCT patient_uuid) as unique_patients,
                    AVG(CASE WHEN ddi_known THEN 1 ELSE 0 END) as pct_known_in_patients
                FROM patient_ddi_collapsed_from_topk
                WHERE pair_key IS NOT NULL
                GROUP BY pair_key
            )
            SELECT 
                s.pair_key,
                s.drug1_norm,
                s.drug2_norm,
                s.unified_severity,
                s.unified_mechanism_text,
                s.ddi_confidence as static_confidence,
                COALESCE(p.patient_case_count, 0) as patient_cases,
                COALESCE(p.unique_patients, 0) as unique_patients,
                COALESCE(p.pct_known_in_patients, 0) as pct_known_in_patients
            FROM static_ddi s
            LEFT JOIN patient_counts p ON s.pair_key = p.pair_key
            ORDER BY patient_cases DESC, s.unified_severity DESC
        """)
        
        result = db.execute(query)
        rows = result.fetchall()
        
        if not rows:
            print("   ❌ No static DDI data found")
            return
        
        # Convert to DataFrame for better display
        df = pd.DataFrame(rows, columns=[
            'pair_key', 'drug1_norm', 'drug2_norm', 'unified_severity',
            'unified_mechanism_text', 'static_confidence', 'patient_cases',
            'unique_patients', 'pct_known_in_patients'
        ])
        
        print(f"\n✅ Found {len(df)} DDI pairs with static severity")
        print(f"   Total patient cases: {df['patient_cases'].sum():,}")
        print(f"   Pairs with patient cases: {(df['patient_cases'] > 0).sum()}")
        print(f"   Pairs without patient cases: {(df['patient_cases'] == 0).sum()}")
        
        # Summary by severity
        print("\n📈 Breakdown by Severity:")
        severity_summary = df.groupby('unified_severity').agg({
            'pair_key': 'count',
            'patient_cases': 'sum',
            'unique_patients': 'sum'
        }).rename(columns={
            'pair_key': 'num_pairs',
            'patient_cases': 'total_cases',
            'unique_patients': 'total_patients'
        }).sort_values('total_cases', ascending=False)
        
        for severity, row in severity_summary.iterrows():
            print(f"   • {severity}: {int(row['num_pairs'])} pairs, "
                  f"{int(row['total_cases'])} cases, {int(row['total_patients'])} patients")
        
        # Top 20 DDI pairs by patient case count
        print("\n🔝 Top 20 DDI Pairs (by patient case count):")
        print("-" * 80)
        
        top_20 = df.head(20)
        for idx, row in top_20.iterrows():
            print(f"\n{idx + 1}. {row['drug1_norm']} + {row['drug2_norm']}")
            print(f"   Pair Key: {row['pair_key']}")
            print(f"   Severity: {row['unified_severity']}")
            print(f"   Patient Cases: {int(row['patient_cases'])} ({int(row['unique_patients'])} unique patients)")
            print(f"   Static Confidence: {row['static_confidence']:.2f}")
            print(f"   % Known in Patients: {row['pct_known_in_patients'] * 100:.1f}%")
            
            # Truncate mechanism if too long
            mechanism = row['unified_mechanism_text']
            if mechanism and len(mechanism) > 80:
                mechanism = mechanism[:77] + "..."
            print(f"   Mechanism: {mechanism or 'N/A'}")
        
        # Save full results to CSV
        output_file = "static_ddi_analysis.csv"
        df.to_csv(output_file, index=False)
        print(f"\n💾 Full results saved to: {output_file}")
        
        # Additional analysis: Pairs with high patient counts but low static confidence
        print("\n⚠️  High Patient Count but Low Static Confidence (< 0.5):")
        print("-" * 80)
        
        low_confidence = df[(df['patient_cases'] >= 10) & (df['static_confidence'] < 0.5)].head(10)
        if len(low_confidence) > 0:
            for idx, row in low_confidence.iterrows():
                print(f"   • {row['drug1_norm']} + {row['drug2_norm']}: "
                      f"{int(row['patient_cases'])} cases, "
                      f"confidence={row['static_confidence']:.2f}, "
                      f"severity={row['unified_severity']}")
        else:
            print("   None found")
        
        # Pairs with no patient cases but marked as severe
        print("\n🚨 Severe DDIs with NO Patient Cases:")
        print("-" * 80)
        
        severe_no_cases = df[(df['unified_severity'].isin(['Major', 'Contraindicated'])) & 
                             (df['patient_cases'] == 0)].head(10)
        if len(severe_no_cases) > 0:
            for idx, row in severe_no_cases.iterrows():
                print(f"   • {row['drug1_norm']} + {row['drug2_norm']}: "
                      f"severity={row['unified_severity']}, "
                      f"confidence={row['static_confidence']:.2f}")
        else:
            print("   None found")
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    analyze_static_ddi()
