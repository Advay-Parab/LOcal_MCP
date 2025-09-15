#!/usr/bin/env python3
"""
Streamlit Chatbot Client for Registration MCP Server
This client connects to the MCP server and provides a user-friendly chat interface.
"""

import streamlit as st
import subprocess
import json
import re
import tempfile
import os
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio

class MCPClient:
    """Client to communicate with MCP server"""
    
    def __init__(self, server_script_path: str = "mcp_server.py"):
        self.server_script_path = server_script_path
        self.message_id = 1
    
    def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool using subprocess with proper initialization"""
        try:
            # Start the MCP server process
            process = subprocess.Popen(
                ["python", self.server_script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Step 1: Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": self.message_id,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "registration-chatbot",
                        "version": "1.0.0"
                    }
                }
            }
            self.message_id += 1
            
            # Send initialize request
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Read initialize response
            init_response_line = process.stdout.readline()
            if not init_response_line:
                stderr_output = process.stderr.read()
                process.terminate()
                return {
                    "success": False,
                    "error": f"MCP Server Error: {stderr_output}"
                }
            
            try:
                init_response = json.loads(init_response_line.strip())
                if "error" in init_response:
                    process.terminate()
                    return {
                        "success": False,
                        "error": f"Initialize failed: {init_response['error']['message']}"
                    }
            except json.JSONDecodeError:
                process.terminate()
                return {
                    "success": False,
                    "error": f"Invalid initialize response: {init_response_line}"
                }
            
            # Step 2: Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            process.stdin.write(json.dumps(initialized_notification) + "\n")
            process.stdin.flush()
            
            # Step 3: Send tool call request
            tool_request = {
                "jsonrpc": "2.0",
                "id": self.message_id,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            self.message_id += 1
            
            process.stdin.write(json.dumps(tool_request) + "\n")
            process.stdin.flush()
            
            # Read tool response
            tool_response_line = process.stdout.readline()
            if not tool_response_line:
                stderr_output = process.stderr.read()
                process.terminate()
                return {
                    "success": False,
                    "error": f"MCP Server Error: {stderr_output}"
                }
            
            # Close stdin to signal end of input
            process.stdin.close()
            
            # Parse the tool response
            try:
                tool_response = json.loads(tool_response_line.strip())
                if "error" in tool_response:
                    process.terminate()
                    return {
                        "success": False,
                        "error": tool_response["error"]["message"]
                    }
                
                # Extract content from MCP response
                result = tool_response.get("result", {})
                if "content" in result and result["content"]:
                    content = result["content"][0].get("text", "")
                    process.terminate()
                    return {
                        "success": True,
                        "content": content
                    }
                
                process.terminate()
                return {
                    "success": True,
                    "content": "Operation completed successfully"
                }
                
            except json.JSONDecodeError:
                process.terminate()
                return {
                    "success": False,
                    "error": f"Invalid JSON response: {tool_response_line}"
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to call MCP tool: {str(e)}"
            }

class RegistrationChatbot:
    """Registration chatbot using MCP server"""
    
    def __init__(self):
        self.mcp_client = MCPClient()
        self.reset_registration()
    
    def reset_registration(self):
        """Reset registration state"""
        if 'registration_state' not in st.session_state:
            st.session_state.registration_state = {
                'step': 'start',
                'name': '',
                'email': '',
                'dob': '',
                'completed': False
            }
    
    def validate_email_format(self, email: str) -> bool:
        """Basic email format validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_date_format(self, date_str: str) -> bool:
        """Basic date format validation"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input and return bot response"""
        user_input = user_input.strip()
        state = st.session_state.registration_state
        
        # Handle special commands
        if user_input.lower() in ['show registrations', 'get all registrations', 'list registrations', 'view all']:
            return self.get_all_registrations()
        
        if user_input.lower() in ['statistics', 'stats', 'show stats']:
            return self.get_statistics()
        
        if user_input.lower().startswith('search '):
            query = user_input[7:].strip()  # Remove 'search ' prefix
            return self.search_registrations(query)
        
        if user_input.lower() in ['start registration', 'register', 'new registration', 'sign up']:
            self.reset_registration()
            st.session_state.registration_state['step'] = 'name'
            return "Great! Let's start your registration. 📝\n\nWhat's your full name?"
        
        if user_input.lower() in ['help', '/help', 'commands']:
            return self.get_help_message()
        
        # Registration flow
        if state['step'] == 'start':
            return self.get_welcome_message()
        
        elif state['step'] == 'name':
            if len(user_input) < 2:
                return "Please enter a valid name (at least 2 characters long)."
            
            state['name'] = user_input
            state['step'] = 'email'
            return f"Nice to meet you, **{user_input}**! 👋\n\nNow, please provide your email address:"
        
        elif state['step'] == 'email':
            if not self.validate_email_format(user_input):
                return ("Please enter a valid email address.\n\n"
                       "**Format:** user@example.com")
            
            state['email'] = user_input
            state['step'] = 'dob'
            return ("Perfect! 📧\n\nNow please enter your date of birth.\n\n"
                   "**Format:** YYYY-MM-DD (e.g., 1990-05-15)")
        
        elif state['step'] == 'dob':
            if not self.validate_date_format(user_input):
                return ("Please enter a valid date in YYYY-MM-DD format.\n\n"
                       "**Example:** 1990-05-15 for May 15, 1990")
            
            state['dob'] = user_input
            state['step'] = 'confirm'
            
            return self.show_confirmation()
        
        elif state['step'] == 'confirm':
            if user_input.lower() in ['confirm', 'yes', 'y', 'correct']:
                return self.complete_registration()
            elif user_input.lower() in ['restart', 'no', 'n', 'edit']:
                self.reset_registration()
                st.session_state.registration_state['step'] = 'name'
                return "Let's start over! 🔄\n\nWhat's your full name?"
            else:
                return ("Please confirm your registration:\n\n"
                       "• Type **'confirm'** to complete registration\n"
                       "• Type **'restart'** to start over")
        
        # Default response
        return ("I didn't understand that. 🤔\n\n"
               "Type **'help'** to see available commands or **'register'** to start a new registration.")
    
    def show_confirmation(self) -> str:
        """Show registration confirmation details"""
        state = st.session_state.registration_state
        
        # Validate the data using MCP server
        validation_result = self.mcp_client.call_mcp_tool(
            "validate_registration_data",
            {
                "name": state['name'],
                "email": state['email'],
                "dob": state['dob']
            }
        )
        
        message = "📋 **Please confirm your registration details:**\n\n"
        message += f"• **Name:** {state['name']}\n"
        message += f"• **Email:** {state['email']}\n"
        message += f"• **Date of Birth:** {state['dob']}\n\n"
        
        if validation_result["success"]:
            # Show validation results
            message += validation_result["content"] + "\n\n"
            
            if "Ready for registration" in validation_result["content"]:
                message += "✅ **Everything looks good!**\n\n"
                message += "• Type **'confirm'** to complete registration\n"
                message += "• Type **'restart'** to start over"
            else:
                message += "❌ **Please fix the issues above before proceeding.**\n\n"
                message += "Type **'restart'** to start over."
        else:
            message += f"⚠️ **Validation Error:** {validation_result['error']}\n\n"
            message += "Type **'restart'** to try again."
        
        return message
    
    def complete_registration(self) -> str:
        """Complete the registration using MCP server"""
        state = st.session_state.registration_state
        
        # Call MCP server to add registration
        result = self.mcp_client.call_mcp_tool(
            "add_registration",
            {
                "name": state['name'],
                "email": state['email'],
                "dob": state['dob']
            }
        )
        
        if result["success"]:
            self.reset_registration()
            return f"🎉 **Registration Completed Successfully!**\n\n{result['content']}\n\n" + \
                   "**What's next?**\n" + \
                   "• Type **'register'** for a new registration\n" + \
                   "• Type **'show registrations'** to view all users\n" + \
                   "• Type **'statistics'** to view registration stats"
        else:
            return f"❌ **Registration Failed**\n\n{result['error']}\n\n" + \
                   "Please try again by typing **'restart'**."
    
    def get_all_registrations(self) -> str:
        """Get all registrations from MCP server"""
        result = self.mcp_client.call_mcp_tool("get_all_registrations", {})
        
        if result["success"]:
            return result["content"]
        else:
            return f"❌ **Error:** {result['error']}"
    
    def search_registrations(self, query: str) -> str:
        """Search registrations using MCP server"""
        if not query:
            return "Please provide a search query.\n\n**Usage:** search [name or email]"
        
        result = self.mcp_client.call_mcp_tool("search_registrations", {"query": query})
        
        if result["success"]:
            return result["content"]
        else:
            return f"❌ **Search Error:** {result['error']}"
    
    def get_statistics(self) -> str:
        """Get registration statistics from MCP server"""
        result = self.mcp_client.call_mcp_tool("get_registration_statistics", {})
        
        if result["success"]:
            return result["content"]
        else:
            return f"❌ **Statistics Error:** {result['error']}"
    
    def get_welcome_message(self) -> str:
        """Get welcome message"""
        return """👋 **Welcome to the Registration System!**

I can help you with:

🆕 **Registration**
• Type **'register'** to start a new registration

📋 **View Data**
• Type **'show registrations'** to view all registered users
• Type **'statistics'** to see registration statistics
• Type **'search [query]'** to search by name or email

❓ **Help**
• Type **'help'** to see all available commands

What would you like to do?"""
    
    def get_help_message(self) -> str:
        """Return help message"""
        return """🤖 **Registration Chatbot Help**

**📝 Registration Commands:**
• `register` or `start registration` - Begin new user registration
• `restart` - Start registration over during the process

**📋 Data Commands:**
• `show registrations` or `list registrations` - View all registered users
• `search [query]` - Search by name or email (e.g., "search john" or "search @gmail")
• `statistics` or `stats` - View registration statistics

**❓ General Commands:**
• `help` or `commands` - Show this help message

**🔄 Registration Process:**
1. **Name** - Provide your full name (2+ characters)
2. **Email** - Enter a valid email address
3. **Date of Birth** - Enter in YYYY-MM-DD format (e.g., 1990-05-15)
4. **Confirmation** - Review and confirm your details

**💡 Tips:**
• All data is stored locally in a CSV file
• Email addresses must be unique
• Use natural language - I understand variations of commands

What would you like to do?"""

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Registration Chatbot - MCP Powered",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Registration Chatbot")
    st.markdown("*Powered by Model Context Protocol (MCP) Server*")
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = RegistrationChatbot()
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        welcome_msg = st.session_state.chatbot.get_welcome_message()
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.spinner("Processing..."):
            response = st.session_state.chatbot.process_user_input(prompt)
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
    
    # Sidebar
    with st.sidebar:
        st.header("🛠️ MCP Server Info")
        
        # Server status
        st.subheader("📡 Connection Status")
        try:
            # Test connection by calling a simple MCP tool
            test_result = st.session_state.chatbot.mcp_client.call_mcp_tool("get_registration_statistics", {})
            if test_result["success"]:
                st.success("🟢 MCP Server: Connected")
            else:
                st.error("🔴 MCP Server: Error")
        except:
            st.error("🔴 MCP Server: Disconnected")
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📝 Register", use_container_width=True):
                response = st.session_state.chatbot.process_user_input("register")
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col2:
            if st.button("📋 View All", use_container_width=True):
                response = st.session_state.chatbot.process_user_input("show registrations")
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("📊 Statistics", use_container_width=True):
                response = st.session_state.chatbot.process_user_input("statistics")
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col4:
            if st.button("🔄 Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.chatbot.reset_registration()
                welcome_msg = st.session_state.chatbot.get_welcome_message()
                st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
                st.rerun()
        
        st.markdown("---")
        
        # Search functionality
        st.subheader("🔍 Quick Search")
        search_query = st.text_input("Search registrations:", placeholder="Enter name or email...")
        if st.button("Search", use_container_width=True) and search_query:
            response = st.session_state.chatbot.process_user_input(f"search {search_query}")
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        
        st.markdown("---")
        
        # Instructions
        st.subheader("📖 Instructions")
        st.markdown("""
        **1. Start MCP Server:**
        ```bash
        python mcp_server.py
        ```
        
        **2. Available Commands:**
        - `register` - Start registration
        - `show registrations` - View all
        - `search [query]` - Search users
        - `statistics` - View stats
        - `help` - Get help
        
        **3. Registration Format:**
        - **Name:** Any valid name (2+ chars)
        - **Email:** user@domain.com
        - **DOB:** YYYY-MM-DD format
        """)
        
        # File info
        st.subheader("📁 Data Storage")
        csv_file = "user_registrations.csv"
        if os.path.exists(csv_file):
            file_size = os.path.getsize(csv_file)
            st.success(f"✅ CSV file exists ({file_size} bytes)")
        else:
            st.info("ℹ️ CSV file will be created on first registration")

if __name__ == "__main__":
    main()