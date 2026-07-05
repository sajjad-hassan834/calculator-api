import os
import subprocess
import sys
import argparse
from loguru import logger

# Add parent directory to path so we can import app.core.settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.settings import settings

def restore_database(backup_file: str):
    if not os.path.exists(backup_file):
        logger.error(f"Backup file not found: {backup_file}")
        return
        
    logger.info(f"Starting database restore from {backup_file} into {settings.database_name}")
    
    try:
        cmd = [
            "pg_restore",
            "--dbname", settings.database_url,
            "--clean",
            "--if-exists",
            "--no-owner",
            backup_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Restore completed successfully")
        else:
            logger.warning(f"Restore finished with warnings/errors:\n{result.stderr}")
            
    except Exception as e:
        logger.error(f"Error during restore: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore database from a custom format pg_dump backup.")
    parser.add_argument("backup_file", help="Path to the backup file to restore.")
    args = parser.parse_args()
    
    restore_database(args.backup_file)
