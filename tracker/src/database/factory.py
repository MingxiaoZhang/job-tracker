"""
Database factory - creates the appropriate database instance based on configuration.
"""
import os
import sys

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import DATABASE_TYPE, DATABASE_PATH, DYNAMODB_TABLE_NAME


def get_database():
    """
    Factory function to get the appropriate database instance.

    Returns:
        Database instance (either SQLite or DynamoDB based on DATABASE_TYPE)
    """
    if DATABASE_TYPE.lower() == 'dynamodb':
        from src.database.dynamodb import DynamoDatabase
        print(f"Using DynamoDB (table: {DYNAMODB_TABLE_NAME})")
        return DynamoDatabase(table_name=DYNAMODB_TABLE_NAME)
    else:
        from src.database.db import Database
        print(f"Using SQLite (path: {DATABASE_PATH})")
        return Database(db_path=DATABASE_PATH)
