import asyncio
from backend.app.services.storage.factory import get_storage_provider
from io import BytesIO

async def test_storage_connection():
    print("Testing storage connection...")
    storage = get_storage_provider()
    
    try:
        # Test 1: Get file info to verify credentials
        print("\nTest 1: Verifying credentials and storage access...")
        
        # Test 2: Upload a small test file
        print("\nTest 2: Uploading test file...")
        test_content = b"Hello, this is a test file for SimpleS3DMS!"
        test_file = BytesIO(test_content)
        test_path = "test/hello.txt"
        
        file_name = await storage.upload_file(test_file, test_path)
        print(f"Successfully uploaded test file: {file_name}")
        
        # Test 3: Generate download URL
        print("\nTest 3: Generating download URL...")
        url = await storage.generate_download_url(test_path)
        print(f"Download URL for test file: {url}")
        
        # Test 4: Download the file
        print("\nTest 4: Downloading test file...")
        downloaded = await storage.download_file(test_path)
        content = downloaded.read()
        print(f"Downloaded content: {content.decode()}")
        
        # Test 5: Delete the test file
        print("\nTest 5: Cleaning up - deleting test file...")
        await storage.delete_file(test_path)
        print("Successfully deleted test file")
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_storage_connection()) 