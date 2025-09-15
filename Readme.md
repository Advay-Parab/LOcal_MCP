# 🤖 User Registration Chatbot with Local MCP Server

A complete user registration system built with **Model Context Protocol (MCP)** that handles user registration through a conversational chatbot interface. The system stores data locally in CSV format, replacing the need for external services like Google Sheets or Zapier.

## 🎯 **Project Overview**

This project demonstrates how to:
- **Build a local MCP server** from scratch in Python
- **Create conversational AI interfaces** with Streamlit
- **Handle data persistence** with local CSV storage
- **Implement data validation** and error handling
- **Provide rich user interactions** through natural language

## 🏗️ **System Architecture**

```
┌─────────────────┐    HTTP/JSON-RPC    ┌─────────────────┐    CSV Operations    ┌─────────────────┐
│ Streamlit UI    │ ◄─────────────────► │   MCP Server    │ ◄─────────────────► │ user_registrations│
│ (Chat Interface)│                     │ (Python Server) │                     │     .csv         │
└─────────────────┘                     └─────────────────┘                     └─────────────────┘
```

### **Key Components:**
1. **MCP Server** (`registration_mcp_server.py`) - Handles all data operations
2. **Streamlit Chatbot** (`streamlit_chatbot.py`) - Provides user interface
3. **CSV Storage** (`user_registrations.csv`) - Local data persistence

## ✨ **Features**

### **🤖 Conversational Registration**
- Natural language interaction
- Step-by-step data collection (Name → Email → DOB)
- Real-time validation and feedback
- Confirmation before saving

### **📊 Data Management**
- **Add Registrations** - Store new user data
- **View All Registrations** - List all registered users
- **Search Functionality** - Find users by name or email
- **Statistics Dashboard** - View registration analytics
- **Data Validation** - Email format, date validation, duplicate prevention

### **🛠️ Technical Features**
- **Local MCP Server** - No external dependencies
- **CSV Storage** - Simple, portable data format
- **Error Handling** - Comprehensive error messages
- **Real-time Validation** - Immediate feedback on data entry
- **Responsive UI** - Clean, intuitive Streamlit interface

## 📋 **Prerequisites**

- **Python 3.8+**
- **pip** package manager

## 🚀 **Installation & Setup**

### **Step 1: Clone or Download Files**

Create a new directory and save these files:
- `registration_mcp_server.py` - The MCP server
- `streamlit_chatbot.py` - The Streamlit interface

### **Step 2: Install Dependencies**

```bash
# Install MCP SDK for the server
pip install mcp

# Install Streamlit for the chatbot interface
pip install streamlit requests
```

### **Step 3: Start the MCP Server**

Open a terminal and run:
```bash
python registration_mcp_server.py
```

**Expected Output:**
```
🚀 Starting Registration MCP Server...
📁 Data file: user_registrations.csv

🛠️  Available tools:
   • add_registration - Add new user registration
   • get_all_registrations - Retrieve all registrations
   • search_registrations - Search by name or email
   • get_registration_statistics - View registration stats
   • validate_registration_data - Validate data before saving

📚 Available resources:
   • file://user_registrations.csv - Direct CSV file access

✅ Server ready for connections!
   Connect your AI model to use these tools...
```

### **Step 4: Start the Streamlit Chatbot**

Open a **new terminal** and run:
```bash
streamlit run streamlit_chatbot.py
```

The chatbot will open in your browser at `http://localhost:8501`

## 💬 **Usage Guide**

### **Registration Process**
1. **Start Registration**: Type `register` or click the "Register" button
2. **Enter Name**: Provide your full name (minimum 2 characters)
3. **Enter Email**: Provide a valid email address
4. **Enter Date of Birth**: Use YYYY-MM-DD format (e.g., 1990-05-15)
5. **Confirm Details**: Review and confirm your registration

### **Available Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `register` | Start new registration | `register` |
| `show registrations` | View all registered users | `show registrations` |
| `search [query]` | Search by name or email | `search john` or `search @gmail` |
| `statistics` | View registration statistics | `statistics` |
| `help` | Show available commands | `help` |

### **Example Conversation Flow**

```
User: register
Bot: Great! Let's start your registration. 📝
     What's your full name?

User: John Doe
Bot: Nice to meet you, John Doe! 👋
     Now, please provide your email address:

User: john@example.com
Bot: Perfect! 📧
     Now please enter your date of birth.
     Format: YYYY-MM-DD (e.g., 1990-05-15)

User: 1990-05-15
Bot: 📋 Please confirm your registration details:
     • Name: John Doe
     • Email: john@example.com
     • Date of Birth: 1990-05-15
     
     ✅ Everything looks good!
     • Type 'confirm' to complete registration

User: confirm
Bot: 🎉 Registration Completed Successfully!
     ✅ Successfully registered John Doe
     
     Registration Details:
     • Name: John Doe
     • Email: john@example.com
     • Date of Birth: 1990-05-15
     • Registered: 2025-01-15 14:30:25
```

## 🗂️ **Data Storage**

### **CSV Structure**
Data is stored in `user_registrations.csv` with these columns:

| Column | Description | Example |
|--------|-------------|---------|
| Name | User's full name | John Doe |
| Email | Email address | john@example.com |
| Date_of_Birth | Birth date (YYYY-MM-DD) | 1990-05-15 |
| Registration_Date | When registered | 2025-01-15 14:30:25 |

### **Sample CSV Content**
```csv
Name,Email,Date_of_Birth,Registration_Date
John Doe,john@example.com,1990-05-15,2025-01-15 14:30:25
Jane Smith,jane@example.com,1985-03-20,2025-01-15 14:35:12
Mike Johnson,mike@example.com,1992-07-08,2025-01-15 14:40:33
```

## 🔧 **MCP Server Details**

### **Available Tools**

1. **`add_registration`**
   - **Purpose**: Add new user registration
   - **Parameters**: `name`, `email`, `dob`
   - **Validation**: Name length, email format, date format, duplicate email check

2. **`get_all_registrations`**
   - **Purpose**: Retrieve all registered users
   - **Parameters**: None
   - **Returns**: List of all registrations with IDs

3. **`search_registrations`**
   - **Purpose**: Search users by name or email
   - **Parameters**: `query` (search term)
   - **Returns**: Matching registrations

4. **`get_registration_statistics`**
   - **Purpose**: Get registration analytics
   - **Parameters**: None
   - **Returns**: Total count, age demographics, registration dates

5. **`validate_registration_data`**
   - **Purpose**: Validate data without saving
   - **Parameters**: `name`, `email`, `dob`
   - **Returns**: Validation results for each field

### **Data Validation Rules**

| Field | Validation Rules |
|-------|------------------|
| **Name** | • Minimum 2 characters<br>• Maximum 100 characters<br>• Cannot be empty |
| **Email** | • Valid email format (user@domain.com)<br>• Must be unique (no duplicates)<br>• Cannot be empty |
| **Date of Birth** | • YYYY-MM-DD format<br>• Cannot be in the future<br>• Reasonable age limits (0-150 years) |

## 📊 **Features Showcase**

### **🎯 Registration Statistics**
```
📊 Registration Statistics:

📋 Total Registrations: 25
🌐 Unique Email Domains: 12
📅 First Registration: 2025-01-10 09:15:30
🆕 Latest Registration: 2025-01-15 16:45:22
💾 File Size: 1,234 bytes

👥 Age Demographics:
   Average Age: 32.4 years
   Youngest User: 18 years
   Oldest User: 67 years

📁 Data File: user_registrations.csv
```

### **🔍 Search Results**
```
🔍 Search Results for 'john' (3 matches):

1. John Doe
   📧 Email: john@example.com
   🎂 Date of Birth: 1990-05-15
   📅 Registered: 2025-01-15 14:30:25

2. Johnny Smith
   📧 Email: johnny.smith@gmail.com
   🎂 Date of Birth: 1988-11-22
   📅 Registered: 2025-01-14 11:20:15
``

### **Common Issues**

**1. "MCP Server: Disconnected"**
- **Cause**: MCP server not running
- **Solution**: Start the server with `python registration_mcp_server.py`

**2. "Invalid email format"**
- **Cause**: Incorrect email format
- **Solution**: Use format like `user@domain.com`

**3. "Invalid date format"**
- **Cause**: Wrong date format
- **Solution**: Use YYYY-MM-DD format (e.g., `1990-05-15`)

**4. "Email already registered"**
- **Cause**: Duplicate email address
- **Solution**: Use a different email address

**5. "Failed to call MCP tool"**
- **Cause**: Communication issue between client and server
- **Solution**: Restart both the MCP server and Streamlit app

### **File Permissions**
- Ensure the directory is writable (for CSV file creation)
- Check that `user_registrations.csv` isn't locked by another program

### **Port Conflicts**
- MCP server uses stdio communication (no port needed)
- Streamlit uses port 8501 (changeable with `--server.port` flag)

## 📁 **Project Structure**

```
registration-chatbot/
├── registration_mcp_server.py    # MCP server with all tools
├── streamlit_chatbot.py          # Streamlit chat interface
├── user_registrations.csv        # Generated data file
├── README.md                     # This documentation
└── requirements.txt              # Python dependencies (optional)
```

## 🔄 **Extending the System**

### **Adding New Fields**
1. Update `REQUIRED_FIELDS` in the MCP server
2. Add validation in `RegistrationValidator` class
3. Extend the chatbot conversation flow
4. Update CSV operations

### **Database Integration**
Replace CSV operations with database calls:
```python
# Instead of CSV operations
def add_registration(self, name, email, dob):
    # Database insert logic here
    cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (name, email, dob))
```

### **API Integration**
Add external API calls to the MCP server:
```python
@app.list_tools()
async def list_tools():
    return [
        Tool(name="send_email", description="Send welcome email"),
        Tool(name="sync_to_crm", description="Sync to CRM system")
    ]
```

## 🎓 **Learning Outcomes**

After completing this project, you'll understand:

1. **MCP Architecture** - How to build and structure MCP servers
2. **Data Validation** - Implementing robust input validation
3. **Conversational AI** - Creating natural language interfaces
4. **File Operations** - CSV reading, writing, and manipulation
5. **Error Handling** - Comprehensive error management
6. **UI/UX Design** - Building user-friendly chat interfaces

## 📚 **Additional Resources**

- **MCP Documentation**: https://modelcontextprotocol.io/
- **Streamlit Docs**: https://docs.streamlit.io/
- **Python CSV Module**: https://docs.python.org/3/library/csv.html
---

**Happy Coding! 🎉**

Built with ❤️ using **Model Context Protocol**, **Streamlit**, and **Python**
