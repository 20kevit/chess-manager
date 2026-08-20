"""
FIDE File Storage Manager.
Handles downloading, unzipping, and retention of raw FIDE XML files.
"""
import os
import zipfile
import shutil
import requests
from datetime import datetime, timedelta
from flask import current_app
from typing import Optional

class FideStorageManager:
    
    @staticmethod
    def get_period_string() -> str:
        """Returns current period string: YYYY-MM"""
        return datetime.utcnow().strftime("%Y-%m")
    
    @staticmethod
    def download_and_extract_xml() -> Optional[str]:
        """
        Downloads the FIDE XML zip file and extracts it.
        Returns the path to the extracted XML file, or None on failure.
        """
        url = current_app.config.get("FIDE_XML_URL")
        base_dir = current_app.config.get("FIDE_DATA_DIR")
        period = FideStorageManager.get_period_string()
        
        if not url or not base_dir:
            raise ValueError("FIDE configuration missing in config.py")
            
        period_dir = os.path.join(base_dir, period)
        os.makedirs(period_dir, exist_ok=True)
        
        zip_path = os.path.join(period_dir, "players_list_xml.zip")
        xml_path = os.path.join(period_dir, "players_list_xml.xml")
        
        # If already extracted, return it
        if os.path.exists(xml_path):
            return xml_path
            
        try:
            # Stream download to handle large files
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(zip_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            # Extract XML
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Find the XML file inside the zip
                xml_files = [n for n in zip_ref.namelist() if n.endswith('.xml')]
                if not xml_files:
                    raise ValueError("No XML file found in the downloaded zip.")
                zip_ref.extract(xml_files[0], period_dir)
                
                # Rename to standard name if different
                extracted_path = os.path.join(period_dir, xml_files[0])
                if extracted_path != xml_path:
                    os.rename(extracted_path, xml_path)
            
            # Clean up zip file to save space
            os.remove(zip_path)
            
            return xml_path
            
        except Exception as e:
            # Clean up partial files on failure
            if os.path.exists(zip_path):
                os.remove(zip_path)
            current_app.logger.error(f"FIDE download failed: {str(e)}")
            return None

    @staticmethod
    def cleanup_old_files() -> int:
        """
        Deletes period directories older than the retention period.
        Returns the number of deleted directories.
        """
        base_dir = current_app.config.get("FIDE_DATA_DIR")
        retention_days = current_app.config.get("FIDE_RAW_RETENTION_DAYS", 90)
        
        if not base_dir or not os.path.exists(base_dir):
            return 0
            
        deleted_count = 0
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        for dirname in os.listdir(base_dir):
            dir_path = os.path.join(base_dir, dirname)
            if not os.path.isdir(dir_path):
                continue
                
            # Expected format: YYYY-MM
            try:
                # Parse the date (add day 1 to make it a valid date)
                dir_date = datetime.strptime(dirname + "-01", "%Y-%m-%d")
                if dir_date < cutoff_date:
                    shutil.rmtree(dir_path)
                    deleted_count += 1
            except ValueError:
                # Skip directories that don't match the format
                continue
                
        return deleted_count