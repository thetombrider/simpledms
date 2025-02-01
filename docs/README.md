# SimpleS3DMS Documentation

SimpleS3DMS (Simple Document Management System) is a web-based application that allows users to manage, organize, and store documents with categories and tags.

## Table of Contents
1. [System Overview](#system-overview)
2. [Features](#features)
3. [Technical Architecture](#technical-architecture)
4. [Installation](#installation)
5. [Usage Guide](#usage-guide)
6. [API Reference](#api-reference)

## System Overview

SimpleS3DMS consists of two main components:
- A FastAPI backend that handles document storage and retrieval using Backblaze B2
- A Streamlit frontend that provides a user-friendly interface

## Features

### Document Management
- Upload documents with titles and descriptions
- Organize documents using categories and tags
- View and download stored documents
- Delete documents with confirmation

### Categories
- Create categories with custom icons and descriptions
- Delete existing categories
- Default categories provided if none exist

### Tags
- Create tags with custom colors
- Delete existing tags
- Dynamic tag suggestions when uploading documents
- Create new tags on the fly during document upload

### User Dashboard
- View total number of documents and storage used
- See most used categories and tags
- View document distribution by month
- Category and tag usage statistics

## Technical Architecture

### Frontend Structure
```
frontend/
├── main.py                 # Application entry point
└── app/
    ├── api/               # API client code
    │   └── document_api.py
    ├── components/        # Reusable components
    │   ├── navigation.py  # Navigation menu
    │   └── utils.py      # Shared utilities
    └── pages/            # Page implementations
        ├── upload.py     # Document upload
        ├── documents.py  # Document list/management
        ├── config.py     # Categories/tags config
        └── user.py       # User dashboard
```

### Backend Structure
```
backend/
├── main.py               # FastAPI application entry point
├── core/                 # Core functionality
│   ├── config.py        # Configuration management
│   ├── security.py      # Security utilities
│   └── exceptions.py    # Custom exceptions
├── api/                 # API endpoints
│   └── v1/             # API version 1
│       ├── documents.py # Document endpoints
│       ├── categories.py # Category endpoints
│       └── tags.py     # Tag endpoints
├── models/             # Data models
│   ├── document.py    # Document model
│   ├── category.py    # Category model
│   └── tag.py        # Tag model
├── services/          # Business logic
│   ├── storage.py    # B2 storage service
│   ├── document.py   # Document service
│   └── config.py     # Configuration service
└── db/               # Database
    ├── mongodb.py    # MongoDB connection
    └── repositories/ # Data access layer
        ├── document.py
        ├── category.py
        └── tag.py
```

### Key Components

#### Frontend Components

##### API Client (`document_api.py`)
- Handles all communication with the backend
- Implements document CRUD operations
- Manages categories and tags

##### Utils (`utils.py`)
- Provides caching mechanisms for categories and tags
- Handles async operations
- Contains shared constants and utility functions

##### Navigation (`navigation.py`)
- Implements the sidebar navigation menu
- Manages page state and transitions

##### Pages
- **Upload**: Document upload form with category/tag selection
- **Documents**: Document list with filtering and management
- **Config**: Category and tag management
- **User**: Statistics and user dashboard

#### Backend Components

##### API Layer (`api/v1/`)
- RESTful endpoints for documents, categories, and tags
- Input validation and error handling
- Rate limiting and request validation
- API versioning support

##### Services Layer (`services/`)
- **Storage Service**: Manages file operations with B2
  - File upload/download
  - Presigned URL generation
  - Storage cleanup
- **Document Service**: Handles document operations
  - Metadata management
  - Search and filtering
  - Category/tag associations
- **Config Service**: Manages system configuration
  - Category management
  - Tag management
  - System settings

##### Database Layer (`db/`)
- MongoDB connection management
- Repository pattern implementation
- Data access optimization
- Index management

##### Core (`core/`)
- Configuration management
- Security utilities
- Custom exception handling
- Middleware configuration

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
# Backend settings
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=simpledms
B2_KEY_ID=your_key_id
B2_APPLICATION_KEY=your_app_key
B2_BUCKET_NAME=your_bucket

# Frontend settings
API_URL=http://localhost:8080/api/v1
```

## Usage Guide

### Starting the Application

1. Start the backend:
```bash
cd backend
uvicorn main:app --reload --port 8080
```

2. Start the frontend:
```bash
cd frontend
streamlit run main.py
```

### Basic Operations

#### Uploading Documents
1. Click "Upload" in the navigation menu
2. Fill in document details
3. Select or create categories and tags
4. Click "Upload Document"

#### Managing Documents
1. Navigate to "Documents"
2. Use filters to find documents
3. Click on documents to expand details
4. Use download/delete buttons as needed

#### Configuration
1. Go to "Configuration"
2. Add/remove categories and tags
3. Customize icons and colors

## API Reference

### Document Endpoints
- `GET /api/v1/documents/`: List documents
- `POST /api/v1/documents/`: Upload document
- `GET /api/v1/documents/{id}/download`: Get download URL
- `DELETE /api/v1/documents/{id}`: Delete document

### Category Endpoints
- `GET /api/v1/config/categories/`: List categories
- `POST /api/v1/config/categories/`: Create category
- `DELETE /api/v1/config/categories/{name}`: Delete category

### Tag Endpoints
- `GET /api/v1/config/tags/`: List tags
- `POST /api/v1/config/tags/`: Create tag
- `DELETE /api/v1/config/tags/{name}`: Delete tag

## Future Enhancements
- User authentication and authorization
- Advanced search capabilities
- Document versioning
- Sharing and collaboration features
- API key management
- Notification system 