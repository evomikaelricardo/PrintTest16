import requests
import tkinter as tk
from tkinter import messagebox
from database import logging
import json

# Global variable to store authentication state
current_user = None
auth_token = None

def api_auth_request(method, endpoint, headers=None, payload=None):
    """
    A function to handle authentication API requests.
    """
    url = endpoint  # Full URL is provided
    headers = headers or {
        "Content-Type": "application/json"
    }
    TIMEOUT = 10  # seconds
    
    try:
        if method == "POST":
            response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        elif method == "GET":
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()  # Return parsed JSON response

    except requests.exceptions.RequestException as e:
        error_msg = f"Error during {method} request to {endpoint}: {e}"
        logging.error(error_msg)
        return None
    except ValueError as e:
        error_msg = "Invalid JSON response from authentication API."
        logging.error(error_msg)
        return None

def login(username, password):
    """
    Authenticate user with username and password via REST API.
    Returns True if successful, False otherwise.
    """
    global current_user, auth_token
    
    endpoint = "https://mvdev.evosmartlife.net/api/ewms/login"
    payload = {
        "username": username,
        "password": password
    }
    
    logging.info(f"Attempting login for user: {username}")
    
    response = api_auth_request("POST", endpoint, payload=payload)
    
    if response and response.get("status_code") == 200:
        # Login successful
        current_user = username
        auth_token = response.get("data", {}).get("token")  # Store token if provided
        logging.info(f"Login successful for user: {username}")
        return True
    else:
        # Login failed
        error_message = "Invalid username or password."
        if response and "message" in response:
            error_message = response["message"]
        logging.error(f"Login failed for user {username}: {error_message}")
        return False

def logout():
    """
    Logout user via REST API.
    Returns True if successful, False otherwise.
    """
    global current_user, auth_token
    
    endpoint = "https://mvdev.evosmartlife.net/api/ewms/logout"
    headers = {
        "Content-Type": "application/json"
    }
    
    # Add authorization header if we have a token
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    logging.info(f"Attempting logout for user: {current_user}")
    
    response = api_auth_request("POST", endpoint, headers=headers)
    
    # Clear local authentication state regardless of API response
    current_user = None
    auth_token = None
    
    if response and response.get("status_code") == 200:
        logging.info("Logout successful")
        return True
    else:
        # Even if logout API fails, we clear local state
        logging.warning("Logout API call failed, but local state cleared")
        return True  # Return True since local state is cleared

def is_authenticated():
    """
    Check if user is currently authenticated.
    """
    return current_user is not None

def get_current_user():
    """
    Get the current authenticated user.
    """
    return current_user

def get_auth_token():
    """
    Get the current authentication token.
    """
    return auth_token