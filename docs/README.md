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