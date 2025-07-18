# Multi-Tenant_Instagram_Management

A scalable FastAPI-based backend built to assist digital marketing teams and content agencies in automating Instagram content generation, reply formulation and document-driven captioning using Multimodal GenAI(GPT-4o) and Vector Databases.


## Overview

The Multi-Tenant Instagram Manager leverages Retrieval-Augmented Generation (RAG) to generate personalized captions, replies, and responses for Instagram accounts — using historical post data, comments, captions, and brand documentation.

It supports seamless onboarding of new clients and continuous updates to ensure contextual consistency and authenticity for every brand.


## Key Features

### Auto-Knowledge Base Generator
- Builds a **Retrieval-Augmented Generation (RAG)** knowledge base from:
  - Past Instagram posts, captions, and comments
  - Uploaded brand documents
- Uses vector embeddings for semantic search and context-aware generation

### Ingestion Loop with Kafka
- Automates onboarding and continuous updates
- Ingests new Instagram activity and brand content in near real-time
- Ensures the knowledge base stays fresh and relevant

### Reply & Caption Generator
- Contextual generation based on:
  - Interaction history
  - Brand-specific tone
- Enables rapid, high-quality content creation across accounts


## Tech Stack

- **Python** – Core backend logic
- **FastAPI** – RESTful APIs for interaction
- **LangChain (`TextLoader`, `PyPDFLoader`, etc.)** – RAG pipeline orchestration
- **OpenAI GPT-4o / GPT-3.5-Turbo** - AI models for caption & comment generation 
- **PGVector (PostgreSQL extension)** – Vector store for semantic search  
- **SQLAlchemy** – ORM and tenant-aware database operations
- **Instagram Graph API** – Access to Instagram data
- **Uvicorn** – Server for deploying FastAPI app     

## Folder Structure

├── main.py
├── database.py
├── config/
│   └── settings.py
├── controllers/
│   ├── caption/
│   │   ├── ingest.py
│   │   └── generate_caption.py
│   ├── comment/
│   │   ├── ingest.py
│   │   └── generate_reply.py
│   └── documents/
│       └── ingest.py
├── services/
│   ├── facebook_service.py
│   ├── vision_service.py
│   ├── vector_store_service.py
│   └── split_document.py
├── utils/
│   ├── formatter.py
│   └── loader.py
├── models/
│   └── schemas.py
├── requirements.txt
└── README.md


## Example Use Cases
 
- **Marketing Agencies**: Manage social media for multiple clients by ingesting their brand tone, past captions, and documents.
- **Startups**: Quickly bootstrap AI-powered Instagram responses and captions with minimal manual effort.
- **Enterprises**: Enhance customer engagement via consistent, AI-generated responses based on brand tone.


## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/khushi2511/Multi-Tenant_Instagram_Management.git
   cd Multi-Tenant_Instagram_Management
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create and configure `.env` file**

   Create a `.env` file in the root directory and add the following:
   ```env
   OPEN_API_KEY=your_openai_key
   IG_ACCESS_TOKEN=your_facebook_graph_access_token
   VECTOR_DB_URL=your_pgvector_connection_string
   ```

4. **Run the FastAPI app**
   ```bash
   uvicorn main:app --reload
   ```
