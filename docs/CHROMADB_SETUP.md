# ChromaDB Setup Guide

This document provides instructions for setting up and using ChromaDB in the Rajniti project.

## Overview

ChromaDB is a vector database that will be used for storing and querying election data embeddings. The current implementation provides a simple boilerplate setup without a schema, which will be added in future updates.

## Installation

ChromaDB is included in the project dependencies. To install it:

```bash
# Install all project dependencies
pip install -r requirements.txt
```

Or install ChromaDB separately:

```bash
pip install chromadb==0.5.23
```

## Configuration

ChromaDB can be configured using environment variables. Add these to your `.env` file:

```bash
# ChromaDB Configuration
CHROMA_DB_PATH=./chroma_db                    # Path to store ChromaDB data
CHROMA_COLLECTION_NAME=rajniti_embeddings     # Default collection name
```

### Configuration Options

- **CHROMA_DB_PATH**: Directory where ChromaDB will store its data. Default: `./chroma_db`
- **CHROMA_COLLECTION_NAME**: Name of the default collection. Default: `rajniti_embeddings`

## Usage

### Basic Usage

```python
from app.services import ChromaService

# Initialize the service (uses environment variables or defaults)
chroma_service = ChromaService()

# Get the ChromaDB client
client = chroma_service.get_client()

# Get or create a collection
collection = chroma_service.get_collection()

# Health check
health = chroma_service.health_check()
print(health)
# Output: {
#     'status': 'healthy',
#     'db_path': './chroma_db',
#     'collections': ['rajniti_embeddings'],
#     'default_collection': 'rajniti_embeddings'
# }
```

### Custom Configuration

```python
from app.services import ChromaService

# Initialize with custom configuration
chroma_service = ChromaService(
    db_path="/path/to/custom/db",
    collection_name="my_custom_collection"
)
```

### Working with Collections

```python
# Get the default collection
collection = chroma_service.get_collection()

# Get a specific collection by name
custom_collection = chroma_service.get_collection(name="another_collection")

# Collection will be created automatically if it doesn't exist
```

### Health Checks

```python
# Perform a health check
health = chroma_service.health_check()

if health['status'] == 'healthy':
    print(f"ChromaDB is running at {health['db_path']}")
    print(f"Available collections: {health['collections']}")
else:
    print(f"ChromaDB error: {health['error']}")
```

### Cleanup Operations

```python
# Close the connection (clears internal references)
chroma_service.close()

# Reset the database (WARNING: deletes all data!)
chroma_service.reset()
```

## Project Structure

```
rajniti/
├── app/
│   └── services/
│       ├── chroma_service.py    # ChromaDB service implementation
│       └── __init__.py          # Exports ChromaService
├── chroma_db/                   # ChromaDB data directory (gitignored)
├── tests/
│   └── test_chroma_service.py   # ChromaDB service tests
└── .env.example                 # Example environment configuration
```

## Testing

Run the ChromaDB tests:

```bash
# Run all ChromaDB tests
pytest tests/test_chroma_service.py -v

# Run specific test class
pytest tests/test_chroma_service.py::TestChromaServiceInitialization -v

# Run specific test
pytest tests/test_chroma_service.py::TestChromaServiceInitialization::test_init_with_defaults -v
```

## Features

### Current Implementation

- ✅ Basic ChromaDB client initialization
- ✅ Persistent storage configuration
- ✅ Collection management (create, get)
- ✅ Health check functionality
- ✅ Environment-based configuration
- ✅ Reset and cleanup operations
- ✅ Comprehensive test coverage

### Future Enhancements

- ⏳ Schema implementation for election data
- ⏳ Embedding generation for candidates and parties
- ⏳ Semantic search capabilities
- ⏳ Batch operations for bulk data loading
- ⏳ Query and filtering functionality

## Best Practices

1. **Use Environment Variables**: Configure ChromaDB using `.env` file for different environments
2. **Data Directory**: The `chroma_db/` directory is gitignored to prevent committing database files
3. **Connection Management**: Always close the service when done to free up resources
4. **Health Checks**: Use health checks to verify ChromaDB status before operations
5. **Testing**: Use temporary directories for testing to avoid polluting the main database

## Troubleshooting

### Database Path Issues

If you encounter permission errors:
```bash
# Ensure the database directory exists and is writable
mkdir -p ./chroma_db
chmod 755 ./chroma_db
```

### Reset Database

If you need to start fresh:
```python
chroma_service = ChromaService()
chroma_service.reset()  # WARNING: This deletes all data!
```

Or manually:
```bash
rm -rf ./chroma_db
```

### Health Check Failures

If health checks fail:
1. Verify the database path is accessible
2. Check disk space availability
3. Ensure ChromaDB is properly installed
4. Review error messages in health check response

## API Reference

### ChromaService

#### `__init__(db_path=None, collection_name=None)`
Initialize ChromaDB service with optional custom configuration.

#### `get_client() -> chromadb.Client`
Get or create ChromaDB client instance.

#### `get_collection(name=None) -> chromadb.Collection`
Get or create a collection. Creates if it doesn't exist.

#### `health_check() -> dict`
Perform health check and return status information.

#### `reset() -> bool`
Reset ChromaDB client and delete all data. Use with caution!

#### `close() -> None`
Close the ChromaDB client connection and clear references.

## Examples

### Example 1: Basic Health Check Endpoint

```python
from flask import jsonify
from app.services import ChromaService

chroma_service = ChromaService()

@app.route('/api/v1/chroma/health')
def chroma_health():
    health = chroma_service.health_check()
    return jsonify(health)
```

### Example 2: Working with Multiple Collections

```python
from app.services import ChromaService

chroma_service = ChromaService()

# Create collections for different types of data
candidates_col = chroma_service.get_collection(name="candidates")
parties_col = chroma_service.get_collection(name="parties")
constituencies_col = chroma_service.get_collection(name="constituencies")

# Verify all collections were created
health = chroma_service.health_check()
print(f"Collections: {health['collections']}")
```

### Example 3: Integration with Flask App

```python
# In app/__init__.py
from app.services import ChromaService

def create_app():
    app = Flask(__name__)
    
    # Initialize ChromaDB service
    app.chroma_service = ChromaService()
    
    # Verify ChromaDB is healthy on startup
    health = app.chroma_service.health_check()
    if health['status'] == 'healthy':
        print(f"✓ ChromaDB initialized: {health['db_path']}")
    else:
        print(f"✗ ChromaDB error: {health.get('error')}")
    
    return app
```

## Support

For issues or questions:
- Check the test suite for usage examples
- Review the ChromaDB documentation: https://docs.trychroma.com/
- Open an issue on the project repository

## License

This ChromaDB integration is part of the Rajniti project and follows the same MIT license.
