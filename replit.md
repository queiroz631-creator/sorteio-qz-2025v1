# Sorteio QZ - Sistema de Sorteio PWA

## Overview

Sorteio QZ is a Progressive Web Application (PWA) built with Flask for managing lottery-style drawings based on fiscal receipt submissions. Users can register, submit receipts, and generate lucky numbers based on their spending - receiving one lucky number for every R$ 20.00 in validated receipts. The application features a modern, responsive red-themed interface with dark/light mode support and offline capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 for server-side rendering with Bootstrap 5 for responsive UI components
- **Progressive Enhancement**: HTMX for dynamic interactions without full page reloads
- **PWA Features**: Service worker for offline caching, web app manifest for mobile installation
- **Theme System**: CSS custom properties with JavaScript-controlled dark/light mode toggle
- **Styling**: Bootstrap 5 framework with custom CSS using CSS variables for theming

### Backend Architecture
- **Framework**: Flask with Blueprint-based route organization
- **Business Logic**: Separated into dedicated `business/` directory with `SorteioLogic` class
- **Session Management**: Flask sessions for user state persistence using CPF as identifier
- **Error Handling**: Comprehensive try-catch blocks with user-friendly flash messages
- **Validation**: Server-side validation for CPF, phone numbers, and business rules

### Data Storage Solutions
- **Primary Database**: SQL Server with pyodbc driver for production
- **Fallback System**: In-memory data structures for development/testing when database unavailable
- **Connection Management**: Dedicated `DatabaseConnection` class with automatic fallback handling
- **Session Storage**: Flask sessions for temporary user state

### Authentication and Authorization
- **Simple Session-Based**: No complex authentication - users identified by CPF in session
- **Lightweight Security**: Session-based access control for dashboard and user-specific features
- **Data Isolation**: All queries filtered by user's CPF to ensure data separation

### Business Logic Implementation
- **Receipt Processing**: Automatic lucky number generation based on R$ 20.00 threshold
- **Validation Rules**: CPF format validation, phone number validation, receipt value validation
- **Status Management**: Receipt validation status tracking and user participation statistics

## External Dependencies

### CDN Resources
- **Bootstrap 5.3.0**: UI framework for responsive design and components
- **Font Awesome 6.4.0**: Icon library for enhanced visual elements
- **HTMX 1.9.6**: JavaScript library for dynamic HTML interactions

### Database Dependencies
- **SQL Server**: Primary database with pyodbc Python driver
- **ODBC Driver 17**: Required system dependency for SQL Server connectivity

### PWA Infrastructure
- **Service Worker**: Custom implementation for offline caching and background sync
- **Web App Manifest**: Configuration for mobile app installation and branding
- **Cache API**: Browser-native caching for static and dynamic content

### Python Package Dependencies
- **Flask**: Core web framework
- **pyodbc**: SQL Server database connectivity
- **Standard Library**: datetime, logging, os for core functionality

### Development Tools
- **Environment Variables**: SQL Server connection configuration
- **Logging System**: Built-in Python logging for debugging and error tracking
- **Debug Mode**: Flask development server with hot reloading