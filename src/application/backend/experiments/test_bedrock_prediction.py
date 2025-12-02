#!/usr/bin/env python3
"""
Test Bedrock model prediction for a specific drug pair.
Tests the complete prediction pipeline including RAG enrichment and LLM response.
Run: python experiments/test_bedrock_prediction.py
Set AWS credentials before running!
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Force production mode to use RDS
os.environ["ENVIRONMENT"] = "production"

from app.db.session import SessionLocal
from app.schemas.db.prediction import DDIPredictRequest
from app.services.prediction_service import enrich_from_database, invoke_bedrock_model, parse_bedrock_response
from app.schemas.bedrock.bedrock import build_system_prompt, build_user_prompt
import json
import os

def test_bedrock_prediction():
    print("\n🔗 Connecting to database and Bedrock...")
    db = SessionLocal()
    
    try:
        print("\n" + "=" * 80)
        print("BEDROCK PREDICTION TEST")
        print("=" * 80)
        
        # Create test request
        request = DDIPredictRequest(
            drug1="ibuprofen",
            drug2="lisinopril",
            Age=65,
            Sex="M"
        )
        
        print(f"\n📋 Test Request:")
        print(f"   Drug 1: {request.drug1}")
        print(f"   Drug 2: {request.drug2}")
        print(f"   Patient Age: {request.Age}")
        print(f"   Patient Sex: {request.Sex}")
        print(f"   Comorbidities: {request.Comorbidities or 'None'}")
        
        # Step 1: Enrich from database (RAG)
        print("\n📊 Step 1: Enriching context from database (RAG)...")
        enriched_context = enrich_from_database(db, request)
        
        # Step 2: Build prompts
        print("📝 Step 2: Building system and user prompts...")
        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(request, enriched_context)
        
        print(f"\n📤 System Prompt Length: {len(system_prompt)} characters")
        print(f"📤 User Prompt Length: {len(user_prompt)} characters")
        
        # Display the user prompt for inspection
        print(f"\n📋 User Prompt:")
        print("-" * 80)
        print(user_prompt)
        print("-" * 80)
        
        # Step 3: Invoke Bedrock model
        print("\n🤖 Step 3: Calling Bedrock model...")
        print("   (This may take 10-30 seconds...)\n")
        
        completion = invoke_bedrock_model(system_prompt, user_prompt)
        
        # Step 4: Parse response
        print("🔍 Step 4: Parsing model response...")
        parsed_response = parse_bedrock_response(completion)
        
        print("=" * 80)
        print("✅ PREDICTION RESULT")
        print("=" * 80)
        
        # Display enriched context
        print(f"\n📦 Enriched Context (RAG):")
        print(f"   • Similar cases found: {enriched_context.get('similar_cases_count', 0)}")
        print(f"   • Static severity: {enriched_context.get('static_severity', 'Unknown')}")
        print(f"   • Known interaction from patients: {enriched_context.get('known_interaction_from_patients', False)}")
        print(f"   • Average confidence: {enriched_context.get('avg_confidence', 'N/A')}")
        
        mechanisms = enriched_context.get('mechanisms', [])
        if mechanisms:
            print(f"   • Mechanisms ({len(mechanisms)}):")
            for i, mech in enumerate(mechanisms[:3], 1):
                mech_display = mech[:70] + "..." if mech and len(mech) > 70 else (mech or "None")
                print(f"     {i}. {mech_display}")
        
        rep_cases = enriched_context.get('representative_cases', [])
        if rep_cases:
            print(f"\n   • Top 3 similar cases:")
            for i, case in enumerate(rep_cases[:3], 1):
                similarity = case.get('similarity_score', 0)
                similarity_pct = f"{similarity * 100:.1f}%"
                print(f"     {i}. Patient {case.get('patient_uuid', 'N/A')[:20]}... [Similarity: {similarity_pct}]")
                print(f"        Age: {case.get('age')} | Sex: {case.get('sex')} | Confidence: {case.get('confidence')}")
        
        # Display model prediction
        prediction = parsed_response.get('content', {})
        print(f"\n🔮 Model Prediction:")
        print(f"   • Severity: {prediction.get('severity', 'N/A')}")
        print(f"   • Confidence: {prediction.get('confidence', 'N/A')}")
        
        clinical_significance = prediction.get('clinical_significance', 'N/A')
        print(f"\n   📝 Clinical Significance:")
        if clinical_significance and clinical_significance != 'N/A':
            # Wrap text at 80 characters
            lines = clinical_significance.split('\n')
            for line in lines:
                if len(line) <= 76:
                    print(f"      {line}")
                else:
                    # Simple word wrap
                    words = line.split()
                    current_line = "      "
                    for word in words:
                        if len(current_line) + len(word) + 1 <= 80:
                            current_line += word + " "
                        else:
                            print(current_line.rstrip())
                            current_line = "      " + word + " "
                    if current_line.strip():
                        print(current_line.rstrip())
        else:
            print(f"      {clinical_significance}")
        
        recommendations = prediction.get('recommendations', [])
        if recommendations:
            print(f"\n   💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"      {i}. {rec}")
        
        monitoring = prediction.get('monitoring', [])
        if monitoring:
            print(f"\n   🔍 Monitoring:")
            for i, mon in enumerate(monitoring, 1):
                print(f"      {i}. {mon}")
        
        # Display reasoning
        reasoning = parsed_response.get('reasoning', '')
        if reasoning:
            print(f"\n🧠 Model Reasoning:")
            print("-" * 80)
            print(reasoning)
            print("-" * 80)
        
        # Display raw completion for debugging
        print(f"\n📄 Raw Model Completion:")
        print("-" * 80)
        print(completion)
        print("-" * 80)
        
        # Save full result to JSON
        output_file = "bedrock_prediction_result.json"
        result = {
            'request': {
                'drug1': request.drug1,
                'drug2': request.drug2,
                'age': request.Age,
                'sex': request.Sex,
                'comorbidities': request.Comorbidities
            },
            'enriched_context': enriched_context,
            'system_prompt': system_prompt,
            'user_prompt': user_prompt,
            'parsed_response': parsed_response,
            'raw_completion': completion
        }
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n💾 Full result saved to: {output_file}")
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETE")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_bedrock_prediction()
