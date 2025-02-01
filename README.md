# SimpleS3DMS

A simple, scalable Document Management System that uses Amazon S3 for storage. This project aims to provide an easy-to-use solution for personal and home document archival that is both cost-efficient and reliable.

## Features (Phase 1 - Prototype)

- Simple document upload and storage in S3 buckets
- Basic document metadata management
- Simple search functionality
- Basic document categorization
- Document preview for common formats

## Technical Stack (Prototype)

- Backend: Python with FastAPI
  - Boto3 for S3 integration
  - Motor (async MongoDB driver)
  - Beanie (ODM for MongoDB)
  - Python-jose for JWT handling
- Frontend: Streamlit
  - HTTP requests to FastAPI backend
  - Built-in file upload widgets
  - Simple data visualization
- Storage: Amazon S3
- Database: MongoDB (document metadata)

## System Architecture

                                     ┌─────────────────┐
                                     │                 │
                                     │  Amazon S3      │
                                     │  (Storage)      │
                                     │                 │
                                     └────────┬────────┘
                                              │
                                              │
┌─────────────────┐                 ┌────────┴────────┐
│                 │                 │                 │
│    Streamlit    │◄───────────────►│    FastAPI      │
│    Frontend     │                 │    Backend      │
└─────────────────┘                 └────────┬────────┘
                                              │
                                              │
                                     ┌────────┴────────┐
                                     │                 │
                                     │    MongoDB      │
                                     │   (Metadata)    │
                                     │                 │
                                     └─────────────────┘

## Project Structure

We're using a monorepo structure for easier development and deployment:
