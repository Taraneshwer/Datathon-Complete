import hashlib
import logging
import os
import tempfile
import uuid
from datetime import datetime, timedelta
from typing import Any

from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException, status

from app.config import get_settings
from app.db.catalyst import CatalystDBClient

logger = logging.getLogger(__name__)

class StorageService:
    """
    Service for interacting with Zoho Catalyst Stratus Object Storage.
    Handles upload, download, delete, and signed URL generation.
    """

    def __init__(self, db_client: CatalystDBClient):
        self.db_client = db_client
        self.settings = get_settings()
        self.bucket_name = "rainfall-evidence-archive"

    def _get_bucket(self) -> Any:
        try:
            return self.db_client.get_stratus_bucket(self.bucket_name)
        except Exception as e:
            logger.error(f"Failed to get Stratus bucket '{self.bucket_name}': {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Storage service unavailable."
            )

    async def upload_evidence(self, file_content: bytes, original_filename: str, case_id: str) -> dict:
        """
        Uploads a file to Stratus Object Storage.
        Calculates SHA256, generates UUID filename, and returns metadata.
        """
        # Calculate SHA256
        sha256_hash = hashlib.sha256(file_content).hexdigest()
        
        # Generate object name
        ext = os.path.splitext(original_filename)[1]
        object_name = f"evidence/{case_id}/{uuid.uuid4().hex}{ext}"

        # Write to temp file for Catalyst SDK upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        try:
            bucket = self._get_bucket()
            
            upload_result = None
            if hasattr(bucket, "upload_file"):
                upload_result = bucket.upload_file(tmp_path)
            elif hasattr(bucket, "upload"):
                upload_result = bucket.upload(tmp_path)
            else:
                logger.warning("Bucket object does not have upload_file. Using fallback.")
                raise NotImplementedError("Catalyst SDK bucket upload method not recognized.")
            
            # The Catalyst SDK might return a dict or an object with details
            catalyst_file_id = None
            if isinstance(upload_result, dict):
                catalyst_file_id = str(upload_result.get("id") or upload_result.get("file_id"))
            elif hasattr(upload_result, "id"):
                catalyst_file_id = str(getattr(upload_result, "id"))
                
            logger.info(f"Successfully uploaded {object_name} to {self.bucket_name}. Result ID: {catalyst_file_id}")
            
            return {
                "object_name": object_name,
                "bucket_name": self.bucket_name,
                "sha256_hash": sha256_hash,
                "file_size_bytes": len(file_content),
                "upload_status": "success",
                "upload_time": datetime.now(),
                "catalyst_file_id": catalyst_file_id or object_name
            }
        except Exception as e:
            logger.error(f"Stratus upload failed for case {case_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload evidence to storage: {str(e)}"
            )
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    async def delete_evidence(self, identifier: str) -> bool:
        """
        Deletes a file from Stratus Object Storage using its identifier (file_id or object_name).
        """
        if not identifier:
            return False
            
        bucket = self._get_bucket()
        try:
            if hasattr(bucket, "delete_file"):
                bucket.delete_file(identifier)
            elif hasattr(bucket, "delete"):
                bucket.delete(identifier)
            logger.info(f"Deleted evidence object {identifier}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete evidence object {identifier}: {e}")
            return False

    async def download_evidence(self, identifier: str) -> bytes:
        """
        Downloads a file from Stratus Object Storage.
        Returns file content as bytes.
        """
        bucket = self._get_bucket()
        try:
            if hasattr(bucket, "download_file"):
                return bucket.download_file(identifier)
            elif hasattr(bucket, "get_file"):
                return bucket.get_file(identifier)
            else:
                raise NotImplementedError("Catalyst SDK bucket download method not recognized.")
        except Exception as e:
            logger.error(f"Failed to download evidence object {identifier}: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence file not found in storage."
            )

    def generate_download_token(self, evidence_id: str, identifier: str, user_id: str) -> str:
        """
        Generates a time-limited signed JWT for securely downloading an evidence file.
        """
        payload = {
            "evidence_id": evidence_id,
            "identifier": identifier,
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "type": "evidence_download"
        }
        return jwt.encode(payload, self.settings.secret_key, algorithm=self.settings.jwt_algorithm)

    def verify_download_token(self, token: str, evidence_id: str) -> dict:
        """
        Verifies a download token and returns the payload.
        """
        try:
            payload = jwt.decode(token, self.settings.secret_key, algorithms=[self.settings.jwt_algorithm])
            if payload.get("type") != "evidence_download":
                raise ValueError("Invalid token type")
            if payload.get("evidence_id") != str(evidence_id):
                raise ValueError("Token does not match evidence ID")
            return payload
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Download link has expired")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid download link")
