# API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
No authentication required - this is an anonymous idea board.

## Response Format
All API responses follow consistent JSON format with proper HTTP status codes.

### Success Response
- **200 OK**: Successful GET requests
- **201 Created**: Successful POST requests
- **422 Unprocessable Entity**: Validation errors
- **404 Not Found**: Resource not found

## Endpoints

### Health Check
```http
GET /api/
```

**Description**: Health check endpoint to verify API is running.

**Response**:
```json
{
  "message": "Idea Board API is running!"
}
```

---

### Get All Ideas
```http
GET /api/ideas
```

**Description**: Retrieve all ideas sorted by upvote count (descending), then by creation date (newest first).

**Response**:
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "text": "Revolutionary AI that helps with creative brainstorming sessions!",
    "upvotes": 5,
    "created_at": "2024-10-01T12:08:44.435270Z"
  },
  {
    "id": "456e7890-e89b-12d3-a456-426614174001", 
    "text": "Virtual reality platform for collaborative design sessions!",
    "upvotes": 3,
    "created_at": "2024-10-01T13:15:20.123456Z"
  }
]
```

**Status Codes**:
- `200 OK`: Ideas retrieved successfully

---

### Create New Idea
```http
POST /api/ideas
```

**Description**: Submit a new idea to the board.

**Request Body**:
```json
{
  "text": "Your brilliant idea here (max 280 characters)"
}
```

**Validation Rules**:
- `text` is required
- `text` must be between 1 and 280 characters
- `text` cannot be empty or whitespace only

**Response**:
```json
{
  "id": "789e0123-e89b-12d3-a456-426614174002",
  "text": "Your brilliant idea here",
  "upvotes": 0,
  "created_at": "2024-10-01T14:22:33.987654Z"
}
```

**Status Codes**:
- `201 Created`: Idea created successfully
- `422 Unprocessable Entity`: Validation error

**Error Response Example**:
```json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "ensure this value has at most 280 characters",
      "type": "value_error.any_str.max_length",
      "ctx": {"limit_value": 280}
    }
  ]
}
```

---

### Upvote Idea
```http
PATCH /api/ideas/{idea_id}/upvote
```

**Description**: Increment the upvote count for a specific idea.

**Path Parameters**:
- `idea_id` (string, required): The UUID of the idea to upvote

**Response**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "text": "Revolutionary AI that helps with creative brainstorming sessions!",
  "upvotes": 6,
  "created_at": "2024-10-01T12:08:44.435270Z"
}
```

**Status Codes**:
- `200 OK`: Upvote successful
- `404 Not Found`: Idea with specified ID not found

**Error Response Example**:
```json
{
  "detail": "Idea not found"
}
```

## Examples with curl

### Get all ideas
```bash
curl -X GET http://localhost:8000/api/ideas \
  -H "Content-Type: application/json"
```

### Submit new idea
```bash
curl -X POST http://localhost:8000/api/ideas \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Revolutionary blockchain-based voting system for transparent governance!"
  }'
```

### Upvote an idea
```bash
curl -X PATCH http://localhost:8000/api/ideas/123e4567-e89b-12d3-a456-426614174000/upvote \
  -H "Content-Type: application/json"
```

## Rate Limiting
Currently no rate limiting implemented - suitable for demo purposes.

## CORS Configuration
CORS is configured to allow requests from:
- `http://localhost:3000` (development frontend)
- Custom domains as configured in environment variables

## Data Validation
All requests are validated using Pydantic models:

### IdeaCreate Model
```python
class IdeaCreate(BaseModel):
    text: str = Field(..., max_length=280, min_length=1)
```

### Idea Response Model
```python
class IdeaResponse(BaseModel):
    id: str
    text: str
    upvotes: int
    created_at: datetime
```

## Database Schema

### Ideas Collection
```javascript
{
  "_id": ObjectId("..."),  // MongoDB internal ID (not exposed)
  "id": "123e4567-e89b-12d3-a456-426614174000",  // UUID used in API
  "text": "Revolutionary AI that helps with creative brainstorming sessions!",
  "upvotes": 5,
  "created_at": "2024-10-01T12:08:44.435270Z"  // ISO datetime string
}
```

## Interactive Documentation
When running the backend, visit `http://localhost:8000/docs` for interactive Swagger UI documentation with built-in API testing capabilities.
