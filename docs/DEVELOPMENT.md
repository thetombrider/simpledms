# SimpleS3DMS Developer Documentation

This document provides technical details for developers working on the SimpleS3DMS project.

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
pip install -r requirements-dev.txt
```

## Code Organization

### Frontend Architecture

#### State Management
- Uses Streamlit's session state for managing application state
- Cache versioning for categories and tags
- Page navigation state

#### Caching System
```python
# Cache version management in session state
if 'categories_cache_version' not in st.session_state:
    st.session_state.categories_cache_version = 0
if 'tags_cache_version' not in st.session_state:
    st.session_state.tags_cache_version = 0

# Cache decorators with version invalidation
@st.cache_data(ttl=3600)
def get_categories(cache_version: int, _api):
    # Cache is invalidated when cache_version changes
    ...
```

#### Async Operations
The frontend uses a custom async operation handler:
```python
def run_async_operation(func, *args, **kwargs):
    """Helper function to run async operations"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(func(*args, **kwargs))
        return result
    finally:
        loop.close()
        asyncio.set_event_loop(None)
```

### Component Structure

#### API Client
- Handles all HTTP communication with backend
- Implements retry logic and error handling
- Manages file uploads and downloads

#### Navigation
- Sidebar-based navigation
- Form-based buttons to prevent Streamlit rerun issues
- Page state management

#### Utilities
- Shared constants
- Cache management
- File size formatting
- Async operation handling

#### Pages
Each page is a self-contained module with:
- Clear responsibility
- Own state management
- Error handling
- Loading states

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

## Testing

### Manual Testing Checklist
- [ ] Document upload with various file types
- [ ] Category creation and deletion
- [ ] Tag creation and deletion
- [ ] Document filtering
- [ ] Download functionality
- [ ] Delete confirmation flow
- [ ] Cache invalidation
- [ ] Error handling
- [ ] Responsive layout

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

## Deployment

### Development
```bash
streamlit run frontend/main.py
```

### Production
1. Set up environment variables
2. Configure MongoDB
3. Set up B2 bucket
4. Deploy backend (FastAPI)
5. Deploy frontend (Streamlit)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Run tests
5. Submit pull request

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