# Overview

This is a desktop application for generating and printing RFID tags in veterinary or medical environments. The application uses Python with Tkinter for the GUI and connects to an Odoo-based REST API to fetch purchase order data and manage inventory. It automatically detects Zebra printers, generates ZPL (Zebra Programming Language) commands for label printing, and provides a step-by-step interface for selecting purchase orders, items, and printing RFID tags with QR codes.

**Replit Environment**: This application has been adapted to run in the Replit cloud environment. The Windows-specific printer functionality has been replaced with simulation/mocking for demonstration purposes.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **GUI Framework**: Tkinter-based desktop application with custom styling
- **Multi-window Flow**: Step-by-step interface progression from PO selection to item selection to printing
- **Custom Components**: Custom title bars, centered windows, and consistent styling through config-based design patterns
- **Real-time Preview**: ZPL label preview generation using PIL for image processing

## Backend Architecture
- **API Client Pattern**: Centralized API request handling through a reusable `api_request` function
- **Configuration Management**: Environment-based configuration with multiple API endpoints (dev, staging, production)
- **Error Handling**: Global error message management with logging to file
- **Data Flow**: Purchase Order → Items → RFID Tag Generation → Label Printing

## Printing System
- **Printer Detection**: Automatic Zebra printer discovery (simulated in Replit environment)
- **ZPL Generation**: Template-based ZPL code generation for RFID labels with QR codes
- **Print Queue Management**: Asynchronous printing with completion tracking (simulated in Replit)

## Data Models
- **Purchase Orders**: PO number selection and validation
- **Inventory Items**: SKU, item name, and inventory ID management
- **RFID Tags**: Time-based unique tag ID generation with format `YYMMDDHHMMSSXXXX`
- **Label Data**: Expiration dates, QR codes, and formatted text wrapping

## Security
- **User Authentication**: Comprehensive authentication system requiring login before accessing any RFID functionality
- **Protected Windows**: All RFID tag generation windows require successful authentication:
  - "Generate RFID Tag (Step 1 of 2)" - Purchase Order selection
  - "Generate RFID Tag (Step 2 of 2)" - Item selection and printing
  - "Generate RFID tag (Select Printer)" - Printer selection dialog
- **Multiple Entry Point Protection**: Authentication checks in both main.py and individual UI components
- **Session Management**: Logout functionality that clears authentication state and returns to login
- **API Authentication**: Bearer token-based authentication for REST API access
- **Environment Configuration**: API tokens and URLs stored in configuration files
- **Request Timeout**: 10-second timeout protection for API calls

# External Dependencies

## Core Dependencies
- **Tkinter**: Native GUI framework for desktop interface
- **Pillow (PIL)**: Image processing for label previews and icon handling
- **requests**: HTTP client for REST API communication
- **python-decouple**: Environment variable management

## Replit Environment Adaptations
- **Windows-specific dependencies**: Replaced Windows printer libraries (pywin32, wmi) with simulation code
- **Display handling**: Configured for headless/cloud environment compatibility

## UI Enhancement Dependencies
- **tkcalendar**: Date picker component for expiration date selection
- **ttk**: Enhanced Tkinter widgets

## Build and Deployment
- **nuitka**: Python to executable compilation tool
- **imageio**: Additional image processing support

## External Services
- **Odoo REST API**: Primary data source for purchase orders and inventory items
- **Development Environment**: `https://mvdev.evosmartlife.net`
- **Production Environment**: `https://evorfid.petfarma.biz`
- **Local Development**: `https://ewms-dev.indieprojects.com`

## Hardware Integration
- **Zebra Printers**: Direct ZPL command printing for RFID label generation (simulated in Replit)
- **Print Communication**: System-level printer communication (replaced with logging and simulation)

# Replit Setup Notes

## Environment Setup (Current Status - September 18, 2025)
- **Python 3.11**: ✅ Installed and configured
- **Dependencies**: ✅ All requirements installed (requests, pillow, tkcalendar, python-decouple)
- **Requirements.txt**: ✅ Cleaned up and optimized (removed duplicates)
- **Workflow**: ✅ "RFID GUI Application" configured to run `python run_gui.py` with VNC output for GUI display
- **Deployment**: ✅ VM deployment configuration set for persistent state management
- **Import Status**: ✅ FULLY IMPORTED AND FUNCTIONAL - Application runs successfully in Replit environment

## Running the Application
- Use `python run_gui.py` or start the "RFID GUI Application" workflow
- The application runs with simulated printer functionality for demonstration
- All print operations are logged to `app.log` file
- GUI functionality may be limited in cloud environment but core logic remains intact

## Key Adaptations Made
- Replaced Windows printer detection with simulation
- Modified printer communication to use logging instead of actual printing
- Maintained all business logic and API communication
- Preserved ZPL generation and label formatting capabilities
- Configured for VM deployment to maintain application state