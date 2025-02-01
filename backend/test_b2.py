import asyncio
from backend.app.services.b2 import B2Service
from io import BytesIO

async def test_b2_connection():
    print("Testing Backblaze B2 connection...")
    b2_service = B2Service()
    
    try:
        # Test 1: List buckets to verify credentials
        print("\nTest 1: Verifying credentials and bucket access...")
        print(f"Successfully connected to bucket: {b2_service.bucket.name}")
        
        # Test 2: Upload a small test file
        print("\nTest 2: Uploading test file...")
        test_content = b"Hello, this is a test file for SimpleS3DMS!"
        test_file = BytesIO(test_content)
        test_path = "test/hello.txt"
        
        file_name = await b2_service.upload_file(test_file, test_path)
        print(f"Successfully uploaded test file: {file_name}")
        
        # Test 3: Generate download URL
        print("\nTest 3: Generating download URL...")
        url = await b2_service.generate_download_url(test_path)
        print(f"Download URL for test file: {url}")
        
        # Test 4: Download the file
        print("\nTest 4: Downloading test file...")
        downloaded = await b2_service.download_file(test_path)
        content = downloaded.read()
        print(f"Downloaded content: {content.decode()}")
        
        # Test 5: Delete the test file
        print("\nTest 5: Cleaning up - deleting test file...")
        await b2_service.delete_file(test_path)
        print("Successfully deleted test file")
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_b2_connection()) 