# ConnectSphere - Real-time Chat Application

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Redis](https://img.shields.io/badge/Redis-7+-red.svg)
![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)

ConnectSphere is a modern, microservices-based real-time chat application built with FastAPI, WebSockets, and a responsive frontend. The application enables users to create accounts, join chat rooms, and communicate in real-time with seamless performance.

## 🚀 Features

### Core Features
- **User Authentication**: Secure registration and login system with JWT tokens
- **Real-time Chat**: WebSocket-based instant messaging
- **Chat Rooms**: Create and join multiple chat rooms
- **Room Management**: Users can create, join, and leave rooms dynamically
- **Message Persistence**: All messages are stored in PostgreSQL database
- **Responsive Design**: Modern UI that works on desktop and mobile devices

### Advanced Features
- **Token Management**: JWT access and refresh tokens with secure logout
- **Redis Caching**: Optimized performance with Redis caching and pub/sub
- **Role-based Access**: Different user roles within chat rooms (admin, member)
- **Auto-reconnection**: WebSocket auto-reconnection on network issues
- **Connection Status**: Real-time connection status indicators

## 🏗️ Architecture

### Microservices Structure

ConnectSphere follows a microservices architecture with the following services:

1. **Authentication Service** (`auth-service/`)
   - User registration, login, and authentication
   - JWT token generation and validation
   - User profile management
   - Port: 5001

2. **Chat Service** (`chat-service/`)
   - Real-time chat functionality with WebSockets
   - Chat room management
   - Message handling and persistence
   - Port: 5002

3. **Frontend Client** (`client/`)
   - Modern web interface
   - WebSocket client for real-time communication
   - Responsive design with CSS Grid/Flexbox

### Infrastructure
- **PostgreSQL**: Primary database for user data and chat messages
- **Redis**: Caching layer and pub/sub for real-time features
- **Docker**: Containerization for easy deployment
- **PgAdmin**: Database management interface
- **RedisInsight**: Redis management and monitoring

## 📋 System Requirements

- Docker and Docker Compose
- Python 3.9+
- Node.js 16+ (for frontend development)

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ConnectSphere
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file with your configuration values.

3. **Start all services:**
   ```bash
   docker-compose up -d
   ```

4. **Access the application:**
   - Chat Interface: `http://localhost:3000` (or your configured port)
   - Auth API Docs: `http://localhost:5001/docs`
   - Chat API Docs: `http://localhost:5002/docs`
   - PgAdmin: `http://localhost:5050`
   - RedisInsight: `http://localhost:8001`

### Development Setup

1. **Set up environment variables:**
   ```bash
   # Create .env file in each service directory
   POSTGRES_USER=your_db_user
   POSTGRES_PASSWORD=your_db_password
   POSTGRES_DB=connectsphere
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

2. **Run services individually:**
   ```bash
   # Terminal 1: Start database and redis
   docker-compose up db redis

   # Terminal 2: Run auth service
   cd auth-service
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 5001

   # Terminal 3: Run chat service
   cd chat-service
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 5002
   ```

## 📖 API Documentation

### Authentication Service

#### Base URL: `http://localhost:5001/api/v1/auth`

- **POST `/register`** - Register a new user
- **POST `/login`** - User login
- **POST `/logout`** - User logout
- **GET `/refresh`** - Refresh access token

#### User Service

#### Base URL: `http://localhost:5001/api/v1/user`

- **GET `/profile`** - Get user profile

### Chat Service

#### WebSocket URL: `ws://localhost:5002/ws`

- **Room Management**: Create, join, and leave chat rooms
- **Message Sending**: Send messages to specific rooms
- **Real-time Updates**: Receive messages in real-time

#### REST API: `http://localhost:5002`

- **Room Management**: `/room/*` endpoints
- **Message Handling**: `/message/*` endpoints
- **Health Check**: `/health`

## 🎨 Frontend Features

### User Interface
- **Modern Design**: Clean, intuitive interface with Font Awesome icons
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Real-time Updates**: Live message updates without page refresh
- **Error Handling**: Graceful error handling with user-friendly modals

### Chat Functionality
- **Room Management**: Create or join chat rooms
- **Message Input**: Send messages with character limits
- **Connection Status**: Visual indicators for connection state
- **Auto-scroll**: Messages automatically scroll to latest

## 🔧 Configuration

### Environment Variables

#### Auth Service
```bash
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=connectsphere
REDIS_HOST=localhost
REDIS_PORT=6379
ACCESS_TOKEN_EXPIRE=900  # 15 minutes
REFRESH_TOKEN_EXPIRE=7    # 7 days
```

#### Chat Service
```bash
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=connectsphere
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Docker Configuration

The `docker-compose.yml` file defines all services:

```yaml
services:
  auth-service:
    build: ./auth-service
    ports:
      - "5001:5001"
  
  chat-service:
    build: ./chat-service
    ports:
      - "5002:5002"
  
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: connectsphere
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  
  redis:
    image: redis:7-alpine
```

## 🧪 Testing

### Running Tests

1. **Start services:**
   ```bash
   docker-compose up -d db redis
   ```

2. **Run auth service tests:**
   ```bash
   cd auth-service
   python -m pytest tests/
   ```

3. **Run chat service tests:**
   ```bash
   cd chat-service
   python -m pytest tests/
   ```

### Manual Testing

1. **API Testing**: Use the Swagger UI at `/docs` endpoints
2. **WebSocket Testing**: Use browser developer tools or WebSocket testing tools
3. **Integration Testing**: Test full user flows from registration to chat

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure PostgreSQL is running
   - Check environment variables in `.env` file
   - Verify database credentials

2. **Redis Connection Issues**
   - Ensure Redis is running
   - Check Redis host and port configuration
   - Verify Redis connection in application logs

3. **WebSocket Connection Problems**
   - Check if chat service is running on correct port
   - Verify WebSocket URL in frontend configuration
   - Check browser console for connection errors

4. **Docker Issues**
   - Ensure Docker and Docker Compose are installed
   - Check Docker daemon is running
   - Verify port availability

### Logs and Monitoring

- **Application Logs**: Check Docker container logs
- **Database Logs**: Monitor PostgreSQL logs for connection issues
- **Redis Logs**: Check Redis logs for caching issues

## 🔒 Security

### Security Features
- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password hashing
- **Token Expiration**: Automatic token expiration and refresh
- **Input Validation**: Comprehensive input validation and sanitization
- **CORS Protection**: Cross-origin resource sharing protection

### Best Practices
- Use strong, unique passwords for database and Redis
- Regularly update dependencies to latest secure versions
- Use HTTPS in production environments
- Implement rate limiting for API endpoints
- Regular security audits and penetration testing

## 🚀 Deployment

### Production Deployment

1. **Build Docker images:**
   ```bash
   docker-compose build --production
   ```

2. **Deploy to server:**
   ```bash
   docker-compose up -d
   ```

3. **Set up reverse proxy (nginx):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
       
       location /api/v1/auth {
           proxy_pass http://localhost:5001;
       }
       
       location /api/v1/chat {
           proxy_pass http://localhost:5002;
       }
   }
   ```

### Scaling Considerations
- Use multiple instances of auth and chat services
- Implement load balancing with nginx or cloud load balancers
- Use managed database services (AWS RDS, Google Cloud SQL)
- Consider Redis clustering for high availability
- Implement monitoring and alerting systems

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for any changes
- Use meaningful commit messages
- Ensure all tests pass before submitting PRs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI team for the excellent web framework
- SQLAlchemy team for the powerful ORM
- Redis team for the blazing-fast cache
- All contributors and users of this project

## 📞 Support

If you have any questions or need help:
- Create an issue in the repository
- Join our Discord server (if available)
- Email us at support@connectsphere.com

---

**ConnectSphere** - Connecting people through seamless real-time communication! 🎉
