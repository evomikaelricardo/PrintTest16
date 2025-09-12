import requests, logging
from config import BASE_URL, API_TOKEN

# Configure logging
logging.basicConfig(
    filename="app.log",  # Log file name
    level=logging.INFO,  # Log level (ERROR, WARNING, INFO, DEBUG, etc.)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log message format
    datefmt="%Y-%m-%d %H:%M:%S"  # Date format
)

error_msg = None  # Stores the most recent API error message

def get_err_msg():
    return error_msg

# Helper function to handle API requests
def api_request(method, endpoint, headers=None, payload=None, params=None):
    """
    A reusable function to handle API requests.
    """
    global error_msg
    
    # Check if API_TOKEN is None and redirect to login if needed
    if API_TOKEN is None:
        from ui.login_interface import show_login
        show_login()
        return None
    url = f"{BASE_URL}{endpoint}"
    headers = headers or {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    TIMEOUT = 10  # seconds
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        error_msg = None  # Clear error if successful
        return response.json()  # Return parsed JSON response

    except requests.exceptions.RequestException as e:
        error_msg = f"Error during {method} request to {endpoint}: {e}"
        logging.error(error_msg)
    except ValueError:
        error_msg = "Invalid JSON response from API."
        logging.error(error_msg)

    return None

# Function to fetch PO Names from the REST API
def fetch_po_number():
    #endpoint = "/api/ewms/accurate/purchase-orders/active"
    endpoint = "/api/ewms/odoo/purchase-orders/active"

    data = api_request("GET", endpoint)
    logging.info(f"RESPONSE: {data}")
    if data and data.get("status_code") == 200 and "data" in data:
        # Transform API output to match the desired format
        po_numbers = [(po["purchase_order_number"],) for po in data["data"]]
        return sorted(po_numbers, key=lambda x: x[0], reverse=True)  # # Sort the tuples descendingly by the po_number
    else:
        return []
    
# Function to fetch items from the REST API based on the selected PO and warehouse_id
def fetch_items(po_number, warehouse_id):
    #endpoint = "/api/ewms/accurate/purchase-orders/items"
    endpoint = "/api/ewms/odoo/purchase-orders/items"
    params = {"warehouse_id": warehouse_id, "po_number": po_number}

    data = api_request("GET", endpoint, params=params)
    if data and data.get("status_code") == 200 and "data" in data:
        '''
        print(data)
        if isinstance(data["data"], list):
            # Format 1: data["data"] is directly a list of items
            items = data["data"]
        else:
            # Format 2: data["data"] is a dict containing detail_items
            items = data["data"]["detail_items"]
        '''
        # Transform API output to match the desired format
        return [
            {
                "item_id": item["item_id"],
                "sku": item["sku"],
                "item_name": item["name"],
                "unit_name": item["unit_name"],
                "quantity": item["quantity"],
                "receive_item_number": item["receive_item_number"],
                "inventory_id": item.get("inventory_id")
            }
            for item in data["data"]
        ]
    else:
        return []

# Function to insert data into stocks via REST API
def insert_into_stocks(po_number, ri_number, item_id, tag_id, exp_date, inventory_id, warehouse_id):
    #endpoint = "/api/ewms/accurate/stocks/"
    endpoint = "/api/ewms/odoo/stocks/create"

    payload = {
        "purchase_order_number": po_number,
        "receive_item_number": ri_number,
        "item_id": item_id,
        "tag_id": tag_id,
        "exp_date": exp_date,
        "inventory_id": inventory_id,
        "location_id": warehouse_id
    }

    data = api_request("POST", endpoint, payload=payload)
    if not data or data.get("status_code") != 201:  # Assuming 201 Created for successful insertion
        # Log the error and the payload data
        logging.error(
            f"Failed to insert stock. Payload: {payload}, Response: {data.get('message', 'Unknown error') if data else 'No response'}"
        )
        return False
    else:
        # Log successful insertion (optional, for debugging purposes)
        logging.info(f"Successfully inserted stock. Payload: {payload}")
        return True
    
# Function to fetch Warehouse Data from the REST API
def fetch_warehouse():
    endpoint = "/api/ewms/accurate/warehouses"

    data = api_request("GET", endpoint)
    if data and data.get("status_code") == 200 and "data" in data:
        # Extract the list of warehouses
        warehouse_list = data["data"]
        
        # Transform API output to match the desired format
        warehouse_map = {item['name']: item['id'] for item in warehouse_list}
        return warehouse_map
    else:
        return []