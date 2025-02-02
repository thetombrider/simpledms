# SimpleS3DMS

A Simple Document Management System using FastAPI, Streamlit, and B2 Cloud Storage.

## Features

- 📄 Document Upload and Management
  - Support for PDF, DOCX, PPTX files
  - Automatic metadata extraction
  - Categories and tags organization
  - File preview (coming soon)

- 🤖 AI-Powered Features
  - Automatic document categorization
  - Smart tag suggestions
  - Description generation
  - OCR capabilities (coming soon)

- 🔗 Document Sharing
  - Secure share links with expiration
  - URL shortening via is.gd
  - Share management and tracking
  - Automatic cleanup of expired shares

- 🔒 Security
  - Secure B2 Cloud Storage integration
  - Document access control
  - Share link expiration
  - User-based permissions

## Quick Start

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```env
# MongoDB Settings
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=simpledms

# Backblaze B2 Settings
B2_KEY_ID=your_key_id
B2_APPLICATION_KEY=your_app_key
B2_BUCKET_NAME=your_bucket

# API Settings
PROJECT_NAME=SimpleS3DMS
VERSION=0.1.1
API_V1_STR=/api/v1

# AI Settings (Optional)
ANTHROPIC_API_KEY=your_key  # For AI features
```

4. Run the backend:
```bash
cd backend
uvicorn app.main:app --reload --port 8080
```

5. Run the frontend:
```bash
cd frontend
streamlit run main.py
```

## Development Status

Current Version: 0.1.1

### Completed Features (v0.1.1)
- ✅ Basic document upload and management
- ✅ B2 Cloud Storage integration
- ✅ Categories and tags system
- ✅ AI-powered document analysis
- ✅ Document sharing with expiration
- ✅ URL shortening integration
- ✅ Background cleanup of expired shares

### Coming Soon (v0.2.0)
- 🔄 Document OCR
- 🔄 Document preview
- 🔄 Document versioning
- 🔄 Enhanced search functionality

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Manual Setup

If you prefer to run services manually:

1. Start MongoDB:
```bash
brew services start mongodb-community
```

2. Set up Python environment:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Start backend:
```bash
cd backend
uvicorn main:app --reload --port 8080
```

4. Start frontend (in a new terminal):
```bash
cd frontend
streamlit run main.py
```

## Development

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for detailed development documentation.

## Roadmap

See [ROADMAP.md](Roadmap.md) for planned features and improvements.

## License

MIT License - see LICENSE file for details.
``` 