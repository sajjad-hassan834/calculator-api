import os
import subprocess
from datetime import datetime
from loguru import logger
import sys

# Add parent directory to path so we can import app.core.settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.settings import settings

def backup_database():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backup_dir = os.path.join(base_dir, settings.backup_dir)
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"backup_{settings.database_name}_{timestamp}.dump")
    
    logger.info(f"Starting database backup to {backup_file}")
    
    try:
        # Construct pg_dump command based on database_url
        cmd = [
            settings.pg_dump_path,
            "--dbname", settings.database_url,
            "--file", backup_file,
            "--format=custom",
            "--compress=9"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Backup completed successfully: {backup_file}")
        else:
            logger.error(f"Backup failed:\n{result.stderr}")
            
    except Exception as e:
        logger.error(f"Error during backup: {str(e)}")

if __name__ == "__main__":
    backup_database()
