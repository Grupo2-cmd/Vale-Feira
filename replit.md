# Vale Feira - Marketplace Platform

## Overview

Vale Feira is a web-based marketplace platform designed to connect small producers from the Vale do Jequitinhonha region in Minas Gerais, Brazil, with buyers. The platform allows local farmers, artisans, and microentrepreneurs to showcase and sell their products through a responsive web interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Architecture Pattern**: Single-file application structure (app.py) based on provided original code
- **Database**: SQLAlchemy ORM with PostgreSQL (production) and SQLite (fallback)
- **Authentication**: Flask-Login for session management with SHA-256 password hashing
- **File Handling**: Werkzeug for secure file uploads with validation

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap with dark theme (Replit agent theme)
- **Icons**: Font Awesome
- **Responsive Design**: Mobile-first approach with Bootstrap grid system
- **JavaScript**: Vanilla JavaScript for form validation and UI enhancements

### Security Implementation
- **Password Security**: SHA-256 hashing for password storage
- **File Upload Security**: Filename sanitization and file type validation
- **Session Management**: Environment-based secret key configuration

## Key Components

### Models (models.py)
- **Usuario (User)**: Handles user authentication with username, password hash, email, and timestamps
- **Produto (Product)**: Manages product information including name, price, description (incomplete in current version)

### Routes Structure
- **app.py**: Main application file containing all routes:
  - `/`: Homepage with product listing
  - `/login`: User authentication 
  - `/registrar`: User registration
  - `/logout`: User logout
  - `/adicionar_produtos`: Product creation form
  - `/excluir_produto/<id>`: Product deletion
  - `/redefinir_senha`: Password reset functionality

### Templates
- **base.html**: Base template with navigation, Bootstrap styling, and responsive layout
- **login.html**: User authentication interface
- **site.html**: Main product gallery with search and filtering capabilities
- **adicionar_produtos.html**: Product creation form
- **registrar.html**: User registration form
- **redefinir_senha.html**: Password reset interface

### Static Assets
- **CSS**: Custom styling in style.css for enhanced UI/UX
- **JavaScript**: Form validation, image previews, and interactive features
- **Upload Directory**: Configurable static/uploads folder for product images

## Data Flow

### User Authentication Flow
1. User accesses login page
2. Credentials validated against Usuario model using SHA-256 hash comparison
3. Flask-Login manages session state
4. Authenticated users can access protected routes

### Product Management Flow
1. Authenticated users access product creation form
2. Form data validated on client and server side
3. Product images uploaded to configured directory
4. Product data saved to database with user association
5. Products displayed on main gallery with filtering options

### Search and Filter Flow
1. Users access main page with optional query parameters
2. Database queries built dynamically based on filters (category, city, search terms)
3. Results rendered with pagination support
4. Filter options populated from existing product data

## External Dependencies

### Python Packages
- **Flask**: Core web framework
- **Flask-SQLAlchemy**: Database ORM
- **Flask-Login**: User session management
- **Flask-CORS**: Cross-origin resource sharing
- **Werkzeug**: WSGI utilities and security helpers

### Frontend Dependencies
- **Bootstrap**: CSS framework (loaded via CDN)
- **Font Awesome**: Icon library (loaded via CDN)
- **Custom CSS/JS**: Local styling and functionality enhancements

### Database
- **SQLite**: Default database (development)
- **Configurable**: Supports any SQLAlchemy-compatible database via DATABASE_URL environment variable

## Deployment Strategy

### Configuration Management
- Environment variables for sensitive data (SESSION_SECRET, DATABASE_URL)
- Configurable upload directories and file size limits
- Development and production configuration separation

### Production Considerations
- **Proxy Support**: ProxyFix middleware for reverse proxy deployments
- **Database Connection**: Pool recycling and pre-ping for connection stability
- **File Uploads**: 16MB maximum file size limit with secure filename handling
- **CORS**: Enabled for API access from different domains

### Development Setup
- Debug mode enabled in development
- Automatic directory creation for uploads
- SQLite database for local development
- Hot reloading supported

### Security Features
- Session secret key configuration
- Secure filename handling for uploads
- Password hashing with SHA-256
- Input validation and sanitization
- CSRF protection through Flask's built-in mechanisms

The application follows Flask best practices with a modular structure that supports scalability and maintainability. The Blueprint-based routing system allows for easy feature expansion, while the SQLAlchemy ORM provides flexibility for different database backends in production environments.