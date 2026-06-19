import os
import boto3
from botocore.exceptions import ClientError
from io import BytesIO


class S3Service:
    def __init__(self):
        self.bucket_name = os.getenv("AWS_S3_BUCKET_NAME", "project-documents")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            "s3",
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
    
    def upload_file(self, file_content: bytes, file_name: str, owner_id: int, project_id: int) -> dict:
        """
        Upload a file to S3 and return metadata.
        
        Returns:
            {
                "key": "s3_key",
                "file_name": "file_name",
                "size": file_size_bytes,
                "url": "s3_url"
            }
        """
        try:
            # S3 key path: owner_id/project_id/file_name
            s3_key = f"{owner_id}/{project_id}/{file_name}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType="application/octet-stream"
            )
            
            # Generate file size
            file_size = len(file_content)
            
            # Generate S3 URL (can be used for direct access if public or signed URL)
            s3_url = f"s3://{self.bucket_name}/{s3_key}"
            
            return {
                "key": s3_key,
                "file_name": file_name,
                "size": file_size,
                "url": s3_url,
            }
        except ClientError as exc:
            raise ValueError(f"Failed to upload file to S3: {exc}")
    
    def download_file(self, s3_key: str) -> bytes:
        """
        Download a file from S3.
        
        Args:
            s3_key: S3 object key (path)
        
        Returns:
            File content as bytes
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response["Body"].read()
        except ClientError as exc:
            raise ValueError(f"Failed to download file from S3: {exc}")
    
    def delete_file(self, s3_key: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            s3_key: S3 object key (path)
        
        Returns:
            True if deletion was successful
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as exc:
            raise ValueError(f"Failed to delete file from S3: {exc}")
    
    def file_exists(self, s3_key: str) -> bool:
        """Check if a file exists in S3."""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "404":
                return False
            raise ValueError(f"Error checking file existence in S3: {exc}")
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for downloading a file from S3.
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
        
        Returns:
            Presigned URL string
        """
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as exc:
            raise ValueError(f"Failed to generate presigned URL: {exc}")
