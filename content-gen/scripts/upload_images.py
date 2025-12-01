"""
Image Upload Script for Content Generation Solution Accelerator.

This script uploads JPG images from the local images folder to Azure Blob Storage.
Uses DefaultAzureCredential for authentication (RBAC).
"""

import asyncio
import os
import sys
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import ContentSettings
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Configuration
STORAGE_ACCOUNT_NAME = os.getenv("AZURE_BLOB_ACCOUNT_NAME", "storagecontentgenjh")
CONTAINER_NAME = os.getenv("AZURE_BLOB_PRODUCT_IMAGES_CONTAINER", "product-images")
IMAGES_FOLDER = Path(__file__).parent / "images"


async def upload_images():
    """Upload all JPG images from the images folder to Azure Blob Storage."""
    
    # Build the blob service URL
    account_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
    
    print(f"Connecting to storage account: {STORAGE_ACCOUNT_NAME}")
    print(f"Target container: {CONTAINER_NAME}")
    print(f"Images folder: {IMAGES_FOLDER}")
    print()
    
    # Create credential and blob service client
    credential = DefaultAzureCredential()
    
    async with BlobServiceClient(account_url=account_url, credential=credential) as blob_service:
        # Get or create container
        container_client = blob_service.get_container_client(CONTAINER_NAME)
        
        try:
            await container_client.create_container()
            print(f"Created container: {CONTAINER_NAME}")
        except Exception as e:
            if "ContainerAlreadyExists" in str(e):
                print(f"Container already exists: {CONTAINER_NAME}")
            else:
                print(f"Note: {e}")
        
        # Find all JPG files
        jpg_files = list(IMAGES_FOLDER.glob("*.jpg")) + list(IMAGES_FOLDER.glob("*.JPG"))
        
        if not jpg_files:
            print("No JPG files found in the images folder.")
            return []
        
        print(f"\nFound {len(jpg_files)} JPG files to upload:")
        print("-" * 50)
        
        uploaded_files = []
        
        for jpg_path in sorted(jpg_files):
            blob_name = jpg_path.name
            blob_client = container_client.get_blob_client(blob_name)
            
            try:
                # Read and upload the image
                with open(jpg_path, "rb") as image_file:
                    image_data = image_file.read()
                
                await blob_client.upload_blob(
                    image_data,
                    overwrite=True,
                    content_settings=ContentSettings(content_type="image/jpeg")
                )
                
                blob_url = f"{account_url}/{CONTAINER_NAME}/{blob_name}"
                uploaded_files.append({
                    "name": blob_name,
                    "url": blob_url,
                    "size": len(image_data)
                })
                
                print(f"  ✓ Uploaded: {blob_name} ({len(image_data):,} bytes)")
                
            except Exception as e:
                print(f"  ✗ Failed to upload {blob_name}: {e}")
        
        print("-" * 50)
        print(f"\nSuccessfully uploaded {len(uploaded_files)} images.")
        
        return uploaded_files


async def list_uploaded_images():
    """List all images in the blob container."""
    
    account_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
    credential = DefaultAzureCredential()
    
    async with BlobServiceClient(account_url=account_url, credential=credential) as blob_service:
        container_client = blob_service.get_container_client(CONTAINER_NAME)
        
        print(f"\nImages in container '{CONTAINER_NAME}':")
        print("-" * 50)
        
        async for blob in container_client.list_blobs():
            print(f"  - {blob.name} ({blob.size:,} bytes)")


async def main():
    """Main entry point."""
    try:
        # Upload images
        uploaded = await upload_images()
        
        if uploaded:
            # List what's in the container
            await list_uploaded_images()
            
            print("\n" + "=" * 50)
            print("Image URLs for use in search index:")
            print("=" * 50)
            for img in uploaded:
                print(f"  {img['url']}")
        
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
