# SimpleS3DMS Developer Documentation

This document provides technical details for developers working on the SimpleS3DMS project.

## Architecture Overview

### Backend (FastAPI)
- RESTful API with FastAPI
- MongoDB with Beanie ODM
- B2 Cloud Storage integration
- Background tasks for maintenance
- AI integration with Claude

### Frontend (Streamlit)
- Modern web interface
- Responsive design
- Real-time updates
- Client-side caching
- Async operations

## Core Components

### Document Management
- File upload handling
- Metadata extraction
- B2 storage integration
- Category and tag management

### AI Integration
- Document analysis
- Category suggestions
- Tag recommendations
- Description generation

### Share System
- Share link generation
- URL shortening via is.gd
- Expiration handling
- Background cleanup

## Development Environment Setup

### Prerequisites
- Python 3.8+
- MongoDB
- Backblaze B2 account
- Git

### Local Development Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`

4. Start services:
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload --port 8080

# Terminal 2 - Frontend
cd frontend
streamlit run main.py
```

## Code Organization

### Backend Structure
```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │   ├── core/
│   │   └── tasks.py
│   │   └── models/
│   │   └── services/
│   │   └── main.py
```

### Frontend Structure
```
frontend/
├── app/
│   ├── api/
│   ├── components/
│   ├── pages/
│   └── utils/
└── main.py
```

## Key Features Implementation

### Document Sharing
```python
# Share creation with URL shortening
async def create_share(document_id: str, owner_id: str, expires_in_days: int) -> Share:
    # Generate B2 download URL
    long_url = await b2_service.generate_download_url(...)
    
    # Create short URL
    try:
        short_url = shortener.isgd.short(long_url)
    except:
        short_url = long_url  # Fallback to long URL
    
    # Create and save share record
    share = Share(
        document_id=doc_id,
        owner_id=owner_id,
        short_url=short_url,
        expires_at=datetime.now(timezone.utc) + timedelta(days=expires_in_days)
    )
    await share.insert()
    return share
```

### Background Tasks
```python
# Cleanup expired shares
async def cleanup_expired_shares():
    while True:
        try:
            await Share.find(
                Share.expires_at < datetime.now(timezone.utc)
            ).delete()
            await asyncio.sleep(3600)  # Run every hour
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
```

## Testing

### Running Tests
```bash
pytest backend/tests/
```

### Test Coverage
```bash
pytest --cov=app backend/tests/
```

## Deployment

### Production Setup
1. Set up MongoDB
2. Configure B2 bucket
3. Set environment variables
4. Deploy using Docker or your preferred method

### Environment Variables
Required environment variables for production:
```env
MONGODB_URL=
MONGODB_DB_NAME=
B2_KEY_ID=
B2_APPLICATION_KEY=
B2_BUCKET_NAME=
ANTHROPIC_API_KEY=  # For AI features
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please ensure:
- Code follows project style
- Tests are included
- Documentation is updated
- Commit messages are clear

## Key Implementation Details

### Document Upload Flow
1. File selection and metadata input
2. Category and tag selection/creation
3. File content reading and size calculation
4. Async upload to backend
5. Success/error handling and state reset

### Category Management
- Icon selection from predefined set
- Optional descriptions
- Cache invalidation on changes
- Default fallback categories

### Tag System
- Dynamic tag creation during upload
- Color customization
- Cache management
- Tag suggestions

### Document List
- Expandable document cards
- Download URL generation
- Delete confirmation flow
- Category and tag filtering

## Error Handling

### Frontend Error Handling
```python
try:
    result = run_async_operation(async_function)
    st.success("Operation successful")
except Exception as e:
    st.error(f"Error: {str(e)}")
```

### API Error Handling
```python
async def api_call():
    try:
        async with await self._get_client() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise  # Propagate to frontend
```

## Development Guidelines

### Code Style
- Follow PEP 8
- Use type hints
- Document functions and classes
- Handle errors gracefully
- Use meaningful variable names

### Best Practices
1. Always invalidate cache when needed
2. Handle async operations properly
3. Provide loading states for long operations
4. Validate input data
5. Handle edge cases
6. Use consistent error messages
7. Keep components focused and modular

### Common Pitfalls
1. Forgetting to invalidate cache
2. Not handling async operations correctly
3. Missing error states
4. Not resetting state after operations
5. Streamlit rerun issues

## Troubleshooting

### Common Issues

1. Cache not updating:
   - Check cache version invalidation
   - Verify cache decorator parameters

2. Navigation issues:
   - Check session state
   - Verify form submit buttons

3. Upload failures:
   - Verify file size
   - Check B2 credentials
   - Validate file type

4. API connection issues:
   - Check API URL
   - Verify backend is running
   - Check network connectivity 