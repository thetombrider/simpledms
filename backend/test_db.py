import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from backend.app.core.config import get_settings

async def test_connection():
    settings = get_settings()
    print(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    try:
        # The ismaster command is cheap and does not require auth.
        await client.admin.command('ismaster')
        print("Successfully connected to MongoDB!")
        
        # List all databases
        database_names = await client.list_database_names()
        print(f"Available databases: {database_names}")
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_connection()) 