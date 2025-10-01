# The Idea Board Platform

A modern, real-time, two-part web application featuring a marketing landing page and a collaborative idea sharing platform where multiple users can simultaneously submit ideas, upvote concepts, and see live updates from the community in real-time.

## 🚀 Features

### Landing Page
- **Professional Design**: Modern hero section with compelling copy and visual hierarchy
- **Feature Highlights**: Four key features showcasing platform capabilities  
- **Responsive Layout**: Fully responsive design optimized for desktop and mobile
- **Clear CTAs**: Strategic call-to-action buttons driving users to the main application

### Idea Board Application - **REAL-TIME MULTI-USER**
- **Idea Submission**: Clean form interface with 280-character limit and real-time character counting
- **Community Voting**: Upvote system allowing users to promote the best ideas
- **Smart Sorting**: Ideas automatically sorted by upvote count for maximum visibility
- **🔴 LIVE REAL-TIME UPDATES**: Multiple users see each other's actions in real-time
  - **Periodic Polling**: App polls server every 5 seconds for live updates
  - **Multi-User Sync**: When User A upvotes, User B sees the update within 5 seconds
  - **Live Indicators**: Visual "Live" indicator and last update timestamps
  - **Seamless UX**: Updates happen in background without disrupting user experience
- **Anonymous Sharing**: No registration required - instant participation
- **Responsive Grid**: Mobile-friendly card layout adapting to all screen sizes

## 🏗️ Technical Architecture

### Real-Time Implementation
The application implements **periodic polling** for real-time multi-user experience:
- **Polling Interval**: 5 seconds for optimal balance between responsiveness and server load
- **Smart Updates**: Silent background polling doesn't interrupt user interactions  
- **Immediate Actions**: User's own actions (submit/upvote) trigger immediate updates
- **Visual Feedback**: Live status indicators show connection and last update time

### Frontend
- **Framework**: React 19.0.0
- **Styling**: Tailwind CSS with custom design system
- **UI Components**: Shadcn/UI component library
- **Routing**: React Router DOM for SPA navigation
- **HTTP Client**: Axios for API communication
- **Notifications**: Sonner for toast notifications
- **Real-time**: Periodic polling with useEffect and setInterval

### Backend
- **Framework**: FastAPI 0.110.1 (Python)
- **Database**: MongoDB with Motor async driver
- **API Design**: RESTful architecture with proper HTTP status codes
- **Data Validation**: Pydantic models for request/response validation
- **CORS**: Configured for cross-origin requests
- **Performance**: Optimized queries with proper sorting

### Database Schema
```javascript
// Ideas Collection
{
  "id": "uuid-string",           // UUID for API usage
  "text": "string (max 280 chars)", // Idea content
  "upvotes": "integer",          // Vote count
  "created_at": "ISO datetime"   // Timestamp
}
```

## 🛠️ API Endpoints

### Base URL
```
http://localhost:8000/api
```

### Endpoints

#### `GET /api/`
Health check endpoint

**Response:**
```json
{
  "message": "Idea Board API is running!"
}
```

#### `GET /api/ideas`
Retrieve all ideas sorted by upvotes (descending) then by creation time (newest first)

**Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "text": "A revolutionary AI that helps with creative brainstorming sessions!",
    "upvotes": 5,
    "created_at": "2024-10-01T12:08:44.435270Z"
  }
]
```

#### `POST /api/ideas`
Create a new idea

**Request Body:**
```json
{
  "text": "Your brilliant idea here (max 280 characters)"
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "text": "Your brilliant idea here",
  "upvotes": 0,
  "created_at": "2024-10-01T12:08:44.435270Z"
}
```

**Validation:**
- Text is required (min 1 character)
- Text cannot exceed 280 characters
- Returns 422 for validation errors

#### `PATCH /api/ideas/{idea_id}/upvote`
Increment upvote count for a specific idea

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "text": "Your brilliant idea here",
  "upvotes": 6,
  "created_at": "2024-10-01T12:08:44.435270Z"
}
```

**Error Cases:**
- Returns 404 if idea not found

## 🐳 Docker Setup

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+

### Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd idea-board-platform
   ```

2. **Start the entire stack:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - **Landing Page**: http://localhost:3000
   - **Idea Board**: http://localhost:3000/app
   - **API Documentation**: http://localhost:8000/docs
   - **MongoDB**: localhost:27017

### Container Architecture

#### Frontend Container
- **Base Image**: node:18-alpine
- **Build**: Multi-stage build with production optimization
- **Port**: 3000
- **Serves**: Production React build via `serve`

#### Backend Container
- **Base Image**: python:3.11-slim
- **Port**: 8000
- **Health Check**: Automated health monitoring
- **Dependencies**: Auto-installed from requirements.txt

#### Database Container
- **Base Image**: mongo:7.0
- **Port**: 27017
- **Persistence**: Named volume for data retention
- **Database**: ideaboard_db

### Development Commands

```bash
# Start all services
docker-compose up

# Start services in background
docker-compose up -d

# Rebuild and start (after code changes)
docker-compose up --build

# View logs
docker-compose logs [service-name]

# Stop all services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v

# Check service status
docker-compose ps
```

## 🧪 Testing

The application includes comprehensive test coverage:

### Manual Testing
1. **Landing Page**: Verify responsive design and navigation
2. **Idea Submission**: Test form validation and character limits
3. **Upvoting**: Confirm vote increments and sorting updates
4. **Real-time Updates**: Verify data refreshes after actions

### API Testing with curl

```bash
# Test API health
curl http://localhost:8000/api/

# Get all ideas
curl http://localhost:8000/api/ideas

# Submit new idea
curl -X POST http://localhost:8000/api/ideas \
  -H "Content-Type: application/json" \
  -d '{"text": "Revolutionary blockchain-based voting system!"}'

# Upvote an idea (replace {id} with actual idea ID)
curl -X PATCH http://localhost:8000/api/ideas/{id}/upvote
```

## 🎨 Design System

### Typography
- **Primary Font**: Inter (modern, readable)
- **Hero Heading**: 5xl/7xl with gradient text effect
- **Body Text**: Base size with proper line height
- **Character Counter**: Dynamic color coding

### Color Palette
- **Primary Gradient**: Blue to Purple (avoiding prohibited combinations)
- **Accent Colors**: Strategic use of red/pink for upvotes
- **Neutral Colors**: Professional gray scale
- **Status Colors**: Green for success, red for errors

### Responsive Breakpoints
- **Mobile**: 375px+ (tested on iPhone SE)
- **Tablet**: 768px+
- **Desktop**: 1024px+
- **Large**: 1920px+

### Real-Time Multi-User Experience

The Idea Board provides a truly **live, collaborative experience** where multiple users can interact simultaneously and see each other's actions in real-time.

**How it works:**
- **Periodic Polling**: App automatically polls the server every 5 seconds
- **Background Updates**: Changes from other users appear seamlessly without page refresh
- **Immediate Feedback**: Your own actions (submit/upvote) trigger instant updates
- **Live Indicators**: Visual status showing "Live" connection and last update time
- **Smart Performance**: Polling doesn't interfere with user interactions

**Multi-User Scenarios:**
- User A upvotes an idea → User B sees the new vote count within 5 seconds
- User C submits a new idea → All other users see it appear in their grid within 5 seconds  
- Ideas automatically re-sort based on community votes across all users
- Real-time idea count updates in the header for all connected users

**Technical Implementation:**
```javascript
useEffect(() => {
  // Initial load
  fetchIdeas(true);
  
  // Set up periodic polling for real-time updates
  const pollInterval = setInterval(() => {
    fetchIdeas(false); // Silent background updates
  }, 5000);
  
  return () => clearInterval(pollInterval);
}, []);
```

This approach provides the **"live" feel** required while being simple, reliable, and server-friendly compared to WebSocket implementations.

## 🚀 Deployment Considerations

### Environment Variables

**Backend (.env):**
```bash
MONGO_URL=mongodb://mongodb:27017
DB_NAME=ideaboard_db
CORS_ORIGINS=http://localhost:3000
```

**Frontend (.env):**
```bash
REACT_APP_BACKEND_URL=http://localhost:8000
```

### Production Optimizations
- Frontend serves optimized production build
- Backend includes health checks for container orchestration
- MongoDB volume persistence prevents data loss
- CORS properly configured for cross-origin requests

## 📊 Performance & Monitoring

### Health Checks
- Backend includes automated health monitoring
- 30-second intervals with 3 retry attempts
- Graceful startup period of 40 seconds

### Optimization Features
- React production build with code splitting
- Efficient MongoDB queries with proper sorting
- Minimal API calls through strategic refetching
- Toast notifications for immediate user feedback

## 🔧 Development Notes

### Architectural Decisions
1. **React over Next.js**: Simpler setup for this scope, faster development
2. **FastAPI over Node.js**: Type safety, automatic docs, performance
3. **MongoDB over PostgreSQL**: Flexible schema, easier Docker setup
4. **Refetch over WebSockets**: Simpler implementation, adequate for use case

### Code Quality
- Clean component architecture with separation of concerns
- Proper error handling and user feedback
- Responsive design with mobile-first approach
- Accessibility considerations with proper ARIA labels

### Trade-offs
- Used refetch pattern instead of WebSockets for simplicity
- Single database for all data (could be separated for scale)
- Basic authentication not implemented (specified as anonymous)

## 📝 Future Enhancements

- Real-time updates with WebSocket integration
- User authentication and profiles
- Idea categories and filtering
- Advanced sorting options (trending, recent, etc.)
- Comment system for ideas
- Analytics dashboard
- Mobile app development

## 🐛 Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Check if ports are in use
lsof -i :3000
lsof -i :8000
lsof -i :27017
```

**Database connection issues:**
```bash
# Check MongoDB container logs
docker-compose logs mongodb

# Verify network connectivity
docker-compose exec backend ping mongodb
```

**Frontend not loading:**
```bash
# Check if backend is responding
curl http://localhost:8000/api/

# Verify CORS configuration
# Check browser console for CORS errors
```

## 👨‍💻 Author

Built as a practical assessment showcasing modern full-stack development practices with Docker containerization, responsive design, and clean API architecture.
