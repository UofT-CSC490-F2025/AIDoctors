#!/usr/bin/env python3
"""
Fetch RDS connection details from AWS SSM and Secrets Manager.
Run: python get_db_connection.py
"""

import boto3
import json
import os

def get_connection_string():
    try:
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        ssm = boto3.client("ssm", region_name=aws_region)
        secrets = boto3.client("secretsmanager", region_name=aws_region)
        
        print("🔍 Fetching RDS connection details from AWS...\n")
        
        # Get connection details from SSM Parameter Store
        host = ssm.get_parameter(Name="/aidoctors/db/host")["Parameter"]["Value"]
        port = ssm.get_parameter(Name="/aidoctors/db/port")["Parameter"]["Value"]
        user = ssm.get_parameter(Name="/aidoctors/db/user")["Parameter"]["Value"]
        dbname = ssm.get_parameter(Name="/aidoctors/db/name")["Parameter"]["Value"]
        schema = ssm.get_parameter(Name="/aidoctors/db/schema")["Parameter"]["Value"]
        
        # Get the secret ARN from SSM
        secret_arn = ssm.get_parameter(Name="/aidoctors/db/password-secret-arn")["Parameter"]["Value"]
        
        # Get password from Secrets Manager
        secret_value = secrets.get_secret_value(SecretId=secret_arn)
        secret_dict = json.loads(secret_value["SecretString"])
        password = secret_dict["password"]
        
        print("=" * 70)
        print("RDS CONNECTION DETAILS")
        print("=" * 70)
        print(f"Host:     {host}")
        print(f"Port:     {port}")
        print(f"Database: {dbname}")
        print(f"Schema:   {schema}")
        print(f"User:     {user}")
        print(f"Password: {password}")
        print("=" * 70)
        
        print("\n📋 PSQL CONNECTION COMMAND:")
        print("=" * 70)
        psql_cmd = f"PGPASSWORD='{password}' psql -h {host} -p {port} -U {user} -d {dbname}"
        print(psql_cmd)
        print("=" * 70)
        
        print("\n🔍 CHECK TABLES:")
        print("=" * 70)
        print(f"After connecting, run:")
        print(f"  SET search_path TO {schema};")
        print(f"  \\dt")
        print(f"  SELECT COUNT(*) FROM patient_ddi_collapsed;")
        print("=" * 70)
        
        print("\n💾 EXPORT AS ENVIRONMENT VARIABLES:")
        print("=" * 70)
        print(f"export PGHOST='{host}'")
        print(f"export PGPORT='{port}'")
        print(f"export PGDATABASE='{dbname}'")
        print(f"export PGUSER='{user}'")
        print(f"export PGPASSWORD='{password}'")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_connection_string()
