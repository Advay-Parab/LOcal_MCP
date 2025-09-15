# User Registration Chatbot with Local MCP Server

This project implements a complete user registration system with a locally hosted MCP server that stores data in a CSV file, replacing the need for Google Sheets and Zapier.

## 🏗️ Architecture

1. **MCP Server** (`mcp_server.py`) - Local HTTP server handling CSV operations
2. **Streamlit Chatbot** (`chatbot_interface.py`) - User interface for registration
3. **CSV Storage** - Local file storage for user registrations

## 📋 Prerequisites

- Python 3.8+
- pip package manager

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the MCP Server

Open a terminal and run:

```bash
python mcp_server.py
```

You should see:
```
MCP Server running on port 8000
Available endpoints:
  POST / - Handle MCP requests
  GET /health - Health check
```

### 3. Start the Streamlit Chatbot

Open a **new terminal** and run:

```bash
streamlit run chatbot_interface.py
```

The chatbot will open in your browser at `http://localhost:8501`

## 🎯 Features

### Registration Process
1. **Name Collection** - Validates minimum 2 characters
2. **Email Validation** - Checks proper email format
3. **Date of Birth** - Validates YYYY-MM-DD format
4. **Confirmation** - Review before saving
5. **CSV Storage** - Saves to local `user_registrations.csv`

### Chatbot Commands
- `register` or `start registration` - Begin new registration
- `show registrations` or `list registrations` - View all registered users
- `help` - Show available commands

### MCP Server API

The server provides these endpoints:

#### Add Registration
```bash
curl -X POST http://localhost:8000 \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add_registration",
    "name": "John Doe",
    "email": "john@example.com",
    "dob": "1990-05-15"
  }'
```

#### Get All Registrations
```bash
curl -X POST http://localhost:8000 \
  -H "Content-Type: application/json" \
  -d '{"action": "get_all_registrations"}'
```

#### Health Check
```bash
curl http://localhost:8000/health
```

## 📁 File Structure

```
project/
├── mcp_server.py           # Local MCP server
├── chatbot_interface.py    # Streamlit chatbot UI
├── requirements.txt        # Python dependencies
├── user_registrations.csv  # Generated CSV file (auto-created)
└── README.md              # This file
```

## 💾 Data Storage

User data is stored in `user_registrations.csv` with these columns:
- **Name** - User's full name
- **Email** - Email address
- **Date_of_Birth** - Birth date (YYYY-MM-DD)
- **Registration_Date** - Timestamp when registered

## 🔧 Troubleshooting

### Connection Issues
- Ensure MCP server is running on port 8000
- Check firewall settings
- Verify both terminals are running

### CSV File Issues
- File is auto-created on first registration
- Check write permissions in the directory
- CSV file location: same directory as `mcp_server.py`

### Common Errors

**"Cannot connect to MCP server"**
- Start the MCP server first: `python mcp_server.py`
- Check if port 8000 is available

**"Invalid email format"**
- Use format: `user@domain.com`

**"Invalid date format"**
- Use format: `YYYY-MM-DD` (e.g., `1990-05-15`)

## 🎮 Usage Examples

### Example Registration Flow

1. **User**: "register"
2. **Bot**: "Great! Let's start your registration. What's your full name?"
3. **User**: "John Doe"
4. **Bot**: "Nice to meet you, John Doe! 👋 Now, please provide your email address:"
5. **User**: "john@example.com"
6. **Bot**: "Great! Now please enter your date of birth in YYYY-MM-DD format:"
7. **User**: "1990-05-15"
8. **Bot**: Shows confirmation with details
9. **User**: "confirm"
10. **Bot**: "🎉 Registration completed successfully!"

### View All Registrations

**User**: "show registrations"

**Bot Response**:
```
📋 All Registrations (2 total):

1. John Doe
   📧 Email: john@example.com
   🎂 DOB: 1990-05-15
   📅 Registered: 2025-01-15 10:30:45

2. Jane Smith
   📧 Email: jane@example.com
   🎂 DOB: 1985-03-20
   📅 Registered: 2025-01-15 10:35:12
```

## 🔄 Extending the System

### Adding New Fields
1. Update CSV headers in `mcp_server.py`
2. Add validation in `chatbot_interface.py`
3. Extend the registration flow

### Database Integration
- Replace CSV operations with database calls
- Maintain the same MCP server API
- Update connection string and queries

### Authentication
- Add user authentication to MCP server
- Implement API key validation
- Secure endpoints with tokens

## 📊 Benefits of This Approach

1. **Local Control** - Full control over data and processing
2. **No External Dependencies** - Works offline, no API limits
3. **Customizable** - Easy to modify and extend
4. **Fast** - Local processing, no network delays
5. **Privacy** - Data stays on your machine
6. **Cost-Effective** - No subscription or API costs

## 🚀 Next Steps

1. Add data validation and error handling
2. Implement user search and filtering
3. Add export functionality (JSON, Excel)
4. Create admin interface for data management
5. Add logging and monitoring
6. Implement backup and restore features