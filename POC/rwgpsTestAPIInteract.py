import requests
from typing import Optional, Dict, List, Union
from datetime import datetime
from dotenv import load_dotenv
import os

class RWGPSRoutes:
    def __init__(self, auth_token: str, api_key: str):
        """
        Initialize with authentication credentials.
        
        Args:
            auth_token (str): Authentication token from get_auth_token()
            api_key (str): RideWithGPS API key
        """
        self.base_url = "https://ridewithgps.com/api/v1"
        self.headers = {
            "x-rwgps-api-key": api_key,
            "x-rwgps-auth-token": auth_token,
            "Content-Type": "application/json"
        }

    def list_routes(self, page: int = 1) -> Optional[Dict]:
        """
        Get a list of routes for the authenticated user.
        
        Args:
            page (int): Page number for pagination
        
        Returns:
            Optional[Dict]: Dictionary containing routes and pagination info,
                          None if request fails
        """
        try:
            url = f"{self.base_url}/routes.json"
            params = {"page": page}
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get routes. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting routes: {str(e)}")
            return None

    def get_route(self, route_id: int) -> Optional[Dict]:
        """
        Get detailed information about a specific route.
        
        Args:
            route_id (int): ID of the route to retrieve
        
        Returns:
            Optional[Dict]: Dictionary containing route details,
                          None if request fails
        """
        try:
            url = f"{self.base_url}/routes/{route_id}.json"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()["route"]
            elif response.status_code == 403:
                print(f"Access forbidden - you don't have permission to view route {route_id}")
                return None
            else:
                print(f"Failed to get route. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting route details: {str(e)}")
            return None

    def display_routes(self) -> List[Dict]:
        """
        Display all routes in a formatted way and return the list for selection.
        
        Returns:
            List[Dict]: List of routes that were displayed
        """
        routes_data = self.list_routes()
        if not routes_data or "routes" not in routes_data:
            print("No routes found or error occurred")
            return []
        
        routes = routes_data["routes"]
        print("\nYour Routes:")
        print("-" * 80)
        print(f"{'ID':<8} {'Name':<30} {'Distance (km)':<12} {'Created':<20}")
        print("-" * 80)
        
        for route in routes:
            distance_km = round(route["distance"] / 1000, 2)
            created_at = datetime.fromisoformat(route["created_at"].replace('Z', '+00:00'))
            created_str = created_at.strftime("%Y-%m-%d %H:%M")
            
            print(f"{route['id']:<8} {route['name'][:30]:<30} {distance_km:<12} {created_str:<20}")
        
        return routes

def save_route_to_file(route: Dict, filename: Optional[str] = None) -> str:
    """
    Save route details to a JSON file.
    
    Args:
        route (Dict): Route data to save
        filename (Optional[str]): Custom filename, if not provided will use route name
    
    Returns:
        str: Path to saved file
    """
    if filename is None:
        # Create filename from route name, replace spaces with underscores
        filename = f"route_{route['id']}_{route['name'].replace(' ', '_')}.json"
    
    import json
    with open(filename, 'w') as f:
        json.dump(route, f, indent=2)
    
    return filename

if __name__ == "__main__":

    # Example usage

    load_dotenv()


    AUTH_TOKEN = os.getenv("RWGPS_APIT")
    API_KEY = os.getenv("RWGPS_APIK")
    
    # Initialize the routes client
    rwgps = RWGPSRoutes(AUTH_TOKEN, API_KEY)
    
    # Display all routes
    routes = rwgps.display_routes()
    
    if routes:
        # Let user select a route
        route_id = int(input("\nEnter the ID of the route you want to download: "))
        
        # Get and save the selected route
        route = rwgps.get_route(route_id)
        if route:
            filename = save_route_to_file(route)
            print(f"\nRoute saved to {filename}")