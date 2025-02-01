# SimpleS3DMS

A Simple Document Management System built with FastAPI and Streamlit.

## Features
- Document upload and management
- Category and tag organization
- B2 storage integration
- MongoDB database
- Modern web interface
- RESTful API

## Prerequisites
- Python 3.8+
- MongoDB
- Backblaze B2 account

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/simpledms.git
cd simpledms
```

2. Set up environment variables in `.env`:
```env
# MongoDB Settings
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=simpledms

# B2 Settings
B2_KEY_ID=your_key_id
B2_APPLICATION_KEY=your_application_key
B2_BUCKET_NAME=your_bucket_name
```

3. Start the application:
```bash
./start.sh
```

The script will:
- Start MongoDB service
- Create and activate virtual environment
- Install dependencies
- Start backend (FastAPI) on port 8080
- Start frontend (Streamlit) on port 8501

Access the application at:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8080

To stop all services, press Ctrl+C in the terminal running the start script.

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

## Technical Architecture

### Frontend Structure
```
frontend/
├── main.py                 # Application entry point
└── app/                    # Main application package
    ├── api/               # API client code
    │   └── document_api.py # API client implementation
    ├── components/        # Reusable components
    │   ├── navigation.py  # Navigation menu
    │   └── utils.py      # Shared utilities and constants
    └── pages/            # Page implementations
        ├── upload.py     # Document upload page
        ├── documents.py  # Document list/management page
        ├── config.py     # Categories/tags configuration
        └── user.py       # User dashboard page
```

### Backend Structure
```
simpledms/                # Root project directory
├── backend/             # Backend application
│   ├── main.py         # FastAPI application entry point
│   └── app/            # Main application package
│       ├── api/        # API endpoints
│       │   └── v1/     # API version 1
│       │       ├── documents.py    # Document endpoints
│       │       ├── categories.py   # Category endpoints
│       │       └── tags.py        # Tag endpoints
│       ├── models/     # Data models
│       │   ├── document.py   # Document model
│       │   ├── category.py   # Category model
│       │   └── tag.py       # Tag model
│       └── services/   # Business logic
│           ├── storage.py    # B2 storage service
│           ├── document.py   # Document service
│           └── config.py     # Configuration service
├── frontend/          # Frontend application (structure as above)
├── docs/             # Documentation
│   ├── README.md     # User documentation
│   └── DEVELOPMENT.md # Developer documentation
├── requirements.txt  # Project dependencies
└── README.md        # Project overview
``` 