"""
Google Cloud Storage Service
Handles file operations using Google Cloud Storage for App Engine deployment
"""

import os
import json
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, BinaryIO
from datetime import datetime

from google.cloud import storage
from google.cloud.exceptions import NotFound


class CloudStorageService:
    """Service for handling file operations with Google Cloud Storage"""
    
    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize the Google Cloud Storage service.
        
        Args:
            bucket_name: Name of the GCS bucket. If None, reads from environment.
        """
        self.bucket_name = bucket_name or os.getenv('GCS_BUCKET_NAME')
        if not self.bucket_name:
            raise ValueError("GCS_BUCKET_NAME must be set in environment variables or provided directly")
        
        # Initialize GCS client (uses Application Default Credentials in App Engine)
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)
    
    def upload_file_from_path(
        self, 
        local_file_path: Union[str, Path], 
        cloud_file_path: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload a file from local filesystem to Cloud Storage.
        
        Args:
            local_file_path: Path to the local file
            cloud_file_path: Destination path in the bucket
            content_type: MIME type of the file (auto-detected if None)
            
        Returns:
            Public URL of the uploaded file
        """
        blob = self.bucket.blob(cloud_file_path)
        
        # Auto-detect content type if not provided
        if content_type is None:
            content_type = self._get_content_type(local_file_path)
        
        blob.upload_from_filename(str(local_file_path), content_type=content_type)
        
        return f"gs://{self.bucket_name}/{cloud_file_path}"
    
    def upload_file_from_memory(
        self,
        file_data: Union[bytes, BinaryIO],
        cloud_file_path: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload file data from memory to Cloud Storage.
        
        Args:
            file_data: File data as bytes or file-like object
            cloud_file_path: Destination path in the bucket
            content_type: MIME type of the file
            
        Returns:
            Public URL of the uploaded file
        """
        blob = self.bucket.blob(cloud_file_path)
        
        if isinstance(file_data, bytes):
            blob.upload_from_string(file_data, content_type=content_type)
        else:
            blob.upload_from_file(file_data, content_type=content_type)
        
        return f"gs://{self.bucket_name}/{cloud_file_path}"
    
    def upload_json(self, data: Dict[str, Any], cloud_file_path: str) -> str:
        """
        Upload JSON data to Cloud Storage.
        
        Args:
            data: Dictionary to save as JSON
            cloud_file_path: Destination path in the bucket
            
        Returns:
            Public URL of the uploaded file
        """
        json_data = json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')
        return self.upload_file_from_memory(json_data, cloud_file_path, 'application/json')
    
    def download_file_to_memory(self, cloud_file_path: str) -> bytes:
        """
        Download a file from Cloud Storage to memory.
        
        Args:
            cloud_file_path: Path to the file in the bucket
            
        Returns:
            File content as bytes
        """
        blob = self.bucket.blob(cloud_file_path)
        
        if not blob.exists():
            raise FileNotFoundError(f"File not found in Cloud Storage: {cloud_file_path}")
        
        return blob.download_as_bytes()
    
    def download_file_to_temp(self, cloud_file_path: str) -> str:
        """
        Download a file from Cloud Storage to a temporary local file.
        
        Args:
            cloud_file_path: Path to the file in the bucket
            
        Returns:
            Path to the temporary local file
        """
        blob = self.bucket.blob(cloud_file_path)
        
        if not blob.exists():
            raise FileNotFoundError(f"File not found in Cloud Storage: {cloud_file_path}")
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        blob.download_to_filename(temp_file.name)
        
        return temp_file.name
    
    def download_json(self, cloud_file_path: str) -> Dict[str, Any]:
        """
        Download and parse JSON data from Cloud Storage.
        
        Args:
            cloud_file_path: Path to the JSON file in the bucket
            
        Returns:
            Parsed JSON data as dictionary
        """
        json_bytes = self.download_file_to_memory(cloud_file_path)
        return json.loads(json_bytes.decode('utf-8'))
    
    def file_exists(self, cloud_file_path: str) -> bool:
        """
        Check if a file exists in Cloud Storage.
        
        Args:
            cloud_file_path: Path to check in the bucket
            
        Returns:
            True if file exists, False otherwise
        """
        blob = self.bucket.blob(cloud_file_path)
        return blob.exists()
    
    def delete_file(self, cloud_file_path: str) -> bool:
        """
        Delete a file from Cloud Storage.
        
        Args:
            cloud_file_path: Path to the file in the bucket
            
        Returns:
            True if file was deleted, False if it didn't exist
        """
        blob = self.bucket.blob(cloud_file_path)
        
        try:
            blob.delete()
            return True
        except NotFound:
            return False
    
    def list_files(self, prefix: str = "", delimiter: str = "/") -> List[str]:
        """
        List files in Cloud Storage with optional prefix.
        
        Args:
            prefix: Prefix to filter files (like directory path)
            delimiter: Delimiter for "directory" structure
            
        Returns:
            List of file paths
        """
        blobs = self.bucket.list_blobs(prefix=prefix, delimiter=delimiter)
        return [blob.name for blob in blobs]
    
    def get_public_url(self, cloud_file_path: str) -> str:
        """
        Get the public URL for a file in Cloud Storage.
        
        Args:
            cloud_file_path: Path to the file in the bucket
            
        Returns:
            Public URL of the file
        """
        blob = self.bucket.blob(cloud_file_path)
        return blob.public_url
    
    def get_signed_url(
        self, 
        cloud_file_path: str, 
        expiration_minutes: int = 60
    ) -> str:
        """
        Generate a signed URL for secure file access.
        
        Args:
            cloud_file_path: Path to the file in the bucket
            expiration_minutes: URL expiration time in minutes
            
        Returns:
            Signed URL for the file
        """
        blob = self.bucket.blob(cloud_file_path)
        
        from datetime import timedelta
        expiration_time = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        
        return blob.generate_signed_url(expiration=expiration_time)
    
    def create_directory_structure(self, paths: List[str]) -> None:
        """
        Create directory-like structure in Cloud Storage by uploading empty files.
        
        Args:
            paths: List of directory paths to create
        """
        for path in paths:
            # Ensure path ends with /
            if not path.endswith('/'):
                path += '/'
            
            # Create an empty file to represent the directory
            directory_marker = path + '.keep'
            self.upload_file_from_memory(b'', directory_marker, 'text/plain')
    
    # Helper methods for specific use cases
    
    def save_cover_image(self, order_id: str, image_data: bytes) -> str:
        """Save book cover image to Cloud Storage."""
        cloud_path = f"covers/cover_{order_id}.png"
        return self.upload_file_from_memory(image_data, cloud_path, 'image/png')
    
    def save_order_data(self, order_id: str, order_data: Dict[str, Any]) -> str:
        """Save order data to Cloud Storage."""
        cloud_path = f"orders/order_{order_id}.json"
        return self.upload_json(order_data, cloud_path)
    
    def save_character_data(self, character_name: str, character_data: Dict[str, Any]) -> str:
        """Save character data to Cloud Storage."""
        # Clean character name for filename
        clean_name = "".join(c for c in character_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_name = clean_name.replace(' ', '_').lower()
        cloud_path = f"characters/{clean_name}.json"
        return self.upload_json(character_data, cloud_path)
    
    def save_book_plan(self, book_title: str, book_plan: Dict[str, Any]) -> str:
        """Save book plan to Cloud Storage."""
        # Clean book title for filename
        clean_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_').lower()
        cloud_path = f"plans/{clean_title}_plan.json"
        return self.upload_json(book_plan, cloud_path)
    
    def save_generated_image(self, book_title: str, image_name: str, image_data: bytes) -> str:
        """Save generated image to Cloud Storage."""
        clean_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_').lower()
        cloud_path = f"images/{clean_title}/{image_name}"
        return self.upload_file_from_memory(image_data, cloud_path, 'image/png')
    
    def _get_content_type(self, file_path: Union[str, Path]) -> str:
        """
        Get MIME content type based on file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MIME type string
        """
        extension = Path(file_path).suffix.lower()
        
        content_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
            '.json': 'application/json',
            '.txt': 'text/plain',
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.zip': 'application/zip',
        }
        
        return content_types.get(extension, 'application/octet-stream') 