"""
Registration MCP Server
A complete MCP server for handling user registrations with CSV storage.
This is specifically designed for the user registration chatbot.
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource
import asyncio
import json
import csv
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

app = Server("registration-server")

REGISTRATION_FILE = "user_registrations.csv"
REQUIRED_FIELDS = ['Name', 'Email', 'Date_of_Birth', 'Registration_Date']

class RegistrationValidator:
    """Validates user registration data"""
    
    @staticmethod
    def validate_name(name: str) -> tuple[bool, str]:
        """Validate name field"""
        if not name or len(name.strip()) < 2:
            return False, "✗ Name must be at least 2 characters long"
        if len(name.strip()) > 100:
            return False, "✗ Name must be less than 100 characters"
        return True, "✓ Valid"
    
    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """Validate email format"""
        if not email:
            return False, "✗ Email is required"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "✗ Invalid email format"
        
        return True, "✓ Valid"
    
    @staticmethod
    def validate_date_of_birth(dob: str) -> tuple[bool, str]:
        """Validate date of birth format and logic"""
        if not dob:
            return False, "✗ Date of birth is required"
        
        try:
            birth_date = datetime.strptime(dob, '%Y-%m-%d')
            today = datetime.now()
            
            #to check if date is not in the future
            if birth_date > today:
                return False, "✗ Date of birth cannot be in the future"
            
            #to check reasonable age limits (0-150 years)
            age = (today - birth_date).days // 365
            if age > 150:
                return False, "✗ Invalid birth date (too old)"
            
            return True, "✓ Valid"
            
        except ValueError:
            return False, "✗ Invalid date format. Use YYYY-MM-DD"

class RegistrationManager:
    """Manages registration data and CSV operations"""
    
    def __init__(self, csv_file: str = REGISTRATION_FILE):
        self.csv_file = csv_file
        self.ensure_csv_exists()
    
    def ensure_csv_exists(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(REQUIRED_FIELDS)
    
    def add_registration(self, name: str, email: str, dob: str) -> Dict[str, Any]:
        """Add a new registration to the CSV file"""
        try:
            #to validate all fields
            name_valid, name_msg = RegistrationValidator.validate_name(name)
            email_valid, email_msg = RegistrationValidator.validate_email(email)
            dob_valid, dob_msg = RegistrationValidator.validate_date_of_birth(dob)
            
            if not all([name_valid, email_valid, dob_valid]):
                errors = []
                if not name_valid:
                    errors.append(f"Name: {name_msg}")
                if not email_valid:
                    errors.append(f"Email: {email_msg}")
                if not dob_valid:
                    errors.append(f"Date of Birth: {dob_msg}")
                
                return {
                    "success": False,
                    "error": "Validation failed",
                    "details": errors
                }
            
            #to check for duplicate email
            if self.email_exists(email):
                return {
                    "success": False,
                    "error": "Email already registered",
                    "details": [f"The email {email} is already registered"]
                }
            
            #to add registration
            registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([name.strip(), email.strip(), dob, registration_date])
            
            return {
                "success": True,
                "message": f"Successfully registered {name.strip()}",
                "data": {
                    "name": name.strip(),
                    "email": email.strip(),
                    "dob": dob,
                    "registration_date": registration_date
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to add registration: {str(e)}"
            }
    
    def get_all_registrations(self) -> Dict[str, Any]:
        """Get all registrations from the CSV file"""
        try:
            registrations = []
            
            if not os.path.exists(self.csv_file):
                return {
                    "success": True,
                    "message": "No registrations found",
                    "count": 0,
                    "data": []
                }
            
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for i, row in enumerate(reader, 1):
                    registrations.append({
                        "id": i,
                        "name": row['Name'],
                        "email": row['Email'],
                        "dob": row['Date_of_Birth'],
                        "registration_date": row['Registration_Date']
                    })
            
            return {
                "success": True,
                "message": f"Found {len(registrations)} registrations",
                "count": len(registrations),
                "data": registrations
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read registrations: {str(e)}"
            }
    
    def search_registrations(self, query: str) -> Dict[str, Any]:
        """Search registrations by name or email"""
        try:
            all_registrations = self.get_all_registrations()
            
            if not all_registrations["success"]:
                return all_registrations
            
            query = query.lower().strip()
            matches = []
            
            for reg in all_registrations["data"]:
                if (query in reg["name"].lower() or 
                    query in reg["email"].lower()):
                    matches.append(reg)
            
            return {
                "success": True,
                "message": f"Found {len(matches)} matches for '{query}'",
                "count": len(matches),
                "data": matches
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to search registrations: {str(e)}"
            }
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists in registrations"""
        try:
            if not os.path.exists(self.csv_file):
                return False
            
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['Email'].lower() == email.lower():
                        return True
            return False
            
        except Exception:
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registration statistics"""
        try:
            all_registrations = self.get_all_registrations()
            
            if not all_registrations["success"] or not all_registrations["data"]:
                return {
                    "success": True,
                    "message": "No statistics available - no registrations found",
                    "data": {
                        "total_registrations": 0,
                        "file_exists": os.path.exists(self.csv_file),
                        "file_size": 0 if not os.path.exists(self.csv_file) else os.path.getsize(self.csv_file)
                    }
                }
            
            registrations = all_registrations["data"]
            
            #to calculate statistics
            total = len(registrations)
            unique_domains = len(set(reg["email"].split("@")[1] for reg in registrations))
            
            #to calculate age statistics
            ages = []
            today = datetime.now()
            
            for reg in registrations:
                try:
                    birth_date = datetime.strptime(reg["dob"], '%Y-%m-%d')
                    age = (today - birth_date).days // 365
                    ages.append(age)
                except:
                    continue
            
            #to calculate registration date statistics
            reg_dates = [datetime.strptime(reg["registration_date"], '%Y-%m-%d %H:%M:%S') for reg in registrations]
            oldest_registration = min(reg_dates).strftime('%Y-%m-%d %H:%M:%S')
            newest_registration = max(reg_dates).strftime('%Y-%m-%d %H:%M:%S')
            
            stats = {
                "total_registrations": total,
                "unique_email_domains": unique_domains,
                "oldest_registration": oldest_registration,
                "newest_registration": newest_registration,
                "file_size_bytes": os.path.getsize(self.csv_file),
                "file_path": self.csv_file
            }
            
            if ages:
                stats.update({
                    "average_age": round(sum(ages) / len(ages), 1),
                    "youngest_user": min(ages),
                    "oldest_user": max(ages)
                })
            
            return {
                "success": True,
                "message": "Statistics calculated successfully",
                "data": stats
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to calculate statistics: {str(e)}"
            }


registration_manager = RegistrationManager()


@app.list_tools()
async def list_tools():
    """List all available registration tools"""
    return [
        Tool(
            name="add_registration",
            description="Add a new user registration with name, email, and date of birth",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full name of the user (2-100 characters)"
                    },
                    "email": {
                        "type": "string",
                        "description": "Valid email address"
                    },
                    "dob": {
                        "type": "string",
                        "description": "Date of birth in YYYY-MM-DD format"
                    }
                },
                "required": ["name", "email", "dob"]
            }
        ),
        Tool(
            name="get_all_registrations",
            description="Retrieve all user registrations from the CSV file",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="search_registrations",
            description="Search registrations by name or email",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (name or email)"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_registration_statistics",
            description="Get statistics about registrations (count, age demographics, etc.)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="validate_registration_data",
            description="Validate registration data without saving",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name to validate"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email to validate"
                    },
                    "dob": {
                        "type": "string",
                        "description": "Date of birth to validate (YYYY-MM-DD)"
                    }
                },
                "required": ["name", "email", "dob"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls from the AI model"""
    
    if name == "add_registration":
        result = registration_manager.add_registration(
            name=arguments.get("name", ""),
            email=arguments.get("email", ""),
            dob=arguments.get("dob", "")
        )
        
        if result["success"]:
            message = f"SUCCESS: {result['message']}\n\nRegistration Details:\n"
            message += f"- Name: {result['data']['name']}\n"
            message += f"- Email: {result['data']['email']}\n"
            message += f"- Date of Birth: {result['data']['dob']}\n"
            message += f"- Registered: {result['data']['registration_date']}"
        else:
            message = f"ERROR: Registration failed: {result['error']}\n"
            if "details" in result:
                message += "\nValidation errors:\n"
                for detail in result["details"]:
                    message += f"- {detail}\n"
        
        return [TextContent(type="text", text=message)]
    
    elif name == "get_all_registrations":
        result = registration_manager.get_all_registrations()
        
        if result["success"]:
            if result["count"] == 0:
                message = "No registrations found yet.\n\nThe registration system is ready to accept new registrations!"
            else:
                message = f"**All Registrations ({result['count']} total):**\n\n"
                for reg in result["data"]:
                    message += f"**{reg['id']}. {reg['name']}**\n"
                    message += f"   Email: {reg['email']}\n"
                    message += f"   Date of Birth: {reg['dob']}\n"
                    message += f"   Registered: {reg['registration_date']}\n\n"
        else:
            message = f"ERROR: Failed to retrieve registrations: {result['error']}"
        
        return [TextContent(type="text", text=message)]
    
    elif name == "search_registrations":
        query = arguments.get("query", "")
        result = registration_manager.search_registrations(query)
        
        if result["success"]:
            if result["count"] == 0:
                message = f"No matches found for '{query}'\n\nTry searching with a different name or email."
            else:
                message = f"**Search Results for '{query}' ({result['count']} matches):**\n\n"
                for reg in result["data"]:
                    message += f"**{reg['id']}. {reg['name']}**\n"
                    message += f"   Email: {reg['email']}\n"
                    message += f"   Date of Birth: {reg['dob']}\n"
                    message += f"   Registered: {reg['registration_date']}\n\n"
        else:
            message = f"ERROR: Search failed: {result['error']}"
        
        return [TextContent(type="text", text=message)]
    
    elif name == "get_registration_statistics":
        result = registration_manager.get_statistics()
        
        if result["success"]:
            stats = result["data"]
            message = "**Registration Statistics:**\n\n"
            message += f"Total Registrations: {stats['total_registrations']}\n"
            
            if stats['total_registrations'] > 0:
                message += f"Unique Email Domains: {stats['unique_email_domains']}\n"
                message += f"First Registration: {stats['oldest_registration']}\n"
                message += f"Latest Registration: {stats['newest_registration']}\n"
                message += f"File Size: {stats['file_size_bytes']} bytes\n"
                
                if 'average_age' in stats:
                    message += f"\n**Age Demographics:**\n"
                    message += f"   Average Age: {stats['average_age']} years\n"
                    message += f"   Youngest User: {stats['youngest_user']} years\n"
                    message += f"   Oldest User: {stats['oldest_user']} years\n"
            else:
                message += "\nNo demographic data available yet."
            
            message += f"\nData File: {stats['file_path']}"
        else:
            message = f"ERROR: Failed to get statistics: {result['error']}"
        
        return [TextContent(type="text", text=message)]
    
    elif name == "validate_registration_data":
        name = arguments.get("name", "")
        email = arguments.get("email", "")
        dob = arguments.get("dob", "")
        
        #to validate each field
        name_valid, name_msg = RegistrationValidator.validate_name(name)
        email_valid, email_msg = RegistrationValidator.validate_email(email)
        dob_valid, dob_msg = RegistrationValidator.validate_date_of_birth(dob)
        
        email_duplicate = registration_manager.email_exists(email) if email_valid else False
        
        message = "**Validation Results:**\n\n"
        
        #to validate name
        message += f"**Name:** {name_msg}\n"
        
        #to validate email
        if email_valid and email_duplicate:
            message += f"**Email:** ✗ Email already registered\n"
        else:
            message += f"**Email:** {email_msg}\n"
        
    # Date of birth validation
        message += f"**Date of Birth:** {dob_msg}\n"
        
        # Overall result
        all_valid = name_valid and email_valid and dob_valid and not email_duplicate
        overall_status = "Ready for registration!" if all_valid else "Fix validation errors before registering"
        message += f"\n**Overall Status:** {overall_status}"
        
        return [TextContent(type="text", text=message)]
    
    else:
        error_message = f"ERROR: Unknown tool: {name}\n\nAvailable tools:\n"
        error_message += "• add_registration\n• get_all_registrations\n"
        error_message += "• search_registrations\n• get_registration_statistics\n• validate_registration_data"
        return [TextContent(type="text", text=error_message)]

# Define resources (optional - allows AI to access the CSV file directly)
@app.list_resources()
async def list_resources():
    """List available resources"""
    return [
        Resource(
            uri=f"file://{REGISTRATION_FILE}",
            name="User Registrations",
            description="CSV file containing all user registrations",
            mimeType="text/csv"
        )
    ]

@app.read_resource()
async def read_resource(uri: str):
    """Read resource content"""
    if uri == f"file://{REGISTRATION_FILE}":
        if os.path.exists(REGISTRATION_FILE):
            with open(REGISTRATION_FILE, 'r', encoding='utf-8') as file:
                content = file.read()
            return [TextContent(type="text", text=content)]
        else:
            return [TextContent(type="text", text="CSV file doesn't exist yet. No registrations found.")]
    else:
        raise ValueError(f"Unknown resource: {uri}")

# Main server runner
async def main():
    """Main function to run the MCP server"""
    print("Starting Registration MCP Server...")
    print(f"Data file: {REGISTRATION_FILE}")
    print("\nAvailable tools:")
    print("   • add_registration - Add new user registration")
    print("   • get_all_registrations - Retrieve all registrations")
    print("   • search_registrations - Search by name or email")
    print("   • get_registration_statistics - View registration stats")
    print("   • validate_registration_data - Validate data before saving")
    print("\nAvailable resources:")
    print(f"   • file://{REGISTRATION_FILE} - Direct CSV file access")
    print("\nServer ready for connections!")
    print("   Connect your AI model to use these tools...")
    
    async with stdio_server() as streams:
        await app.run(
            streams[0], streams[1], app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())