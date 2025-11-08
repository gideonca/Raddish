"""
Example Python client for the Radish HTTP API.
"""

import urllib.request
import urllib.error
import json


class RadishHTTPClient:
    """Simple HTTP client for Radish server using only built-in modules."""
    
    def __init__(self, base_url='http://localhost:8000'):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the HTTP API server
        """
        self.base_url = base_url.rstrip('/')
    
    def _request(self, method, path, data=None):
        """
        Make an HTTP request.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            path: URL path
            data: Optional JSON data for POST requests
            
        Returns:
            Parsed JSON response
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        
        # Prepare request
        headers = {'Content-Type': 'application/json'}
        body = None
        
        if data is not None:
            body = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data)
        except urllib.error.HTTPError as e:
            error_data = e.read().decode('utf-8')
            try:
                return json.loads(error_data)
            except:
                return {'error': error_data}
        except Exception as e:
            return {'error': str(e)}
    
    def ping(self):
        """Test server connection."""
        return self._request('GET', '/ping')
    
    def create_cache(self, cache_name):
        """Create a new cache."""
        return self._request('POST', '/caches', {'name': cache_name})
    
    def list_caches(self):
        """List all caches."""
        return self._request('GET', '/caches')
    
    def delete_cache(self, cache_name):
        """Delete a cache."""
        return self._request('DELETE', f'/cache/{cache_name}')
    
    def cache_set(self, cache_name, key, value):
        """Set a key-value pair in a cache."""
        return self._request('POST', f'/cache/{cache_name}', {'key': key, 'value': value})
    
    def cache_get(self, cache_name, key):
        """Get a value from a cache."""
        return self._request('GET', f'/cache/{cache_name}/{key}')
    
    def cache_get_all(self, cache_name):
        """Get all key-value pairs from a cache."""
        return self._request('GET', f'/cache/{cache_name}')
    
    def cache_delete(self, cache_name, key):
        """Delete a key from a cache."""
        return self._request('DELETE', f'/cache/{cache_name}/{key}')
    
    def cache_keys(self, cache_name):
        """Get all keys in a cache."""
        return self._request('GET', f'/cache/{cache_name}/keys')
    
    def set_value(self, key, value):
        """Set a value in the main store."""
        return self._request('POST', f'/kv/{key}', {'value': value})
    
    def get_value(self, key):
        """Get a value from the main store."""
        return self._request('GET', f'/kv/{key}')
    
    def delete_value(self, key):
        """Delete a key from the main store."""
        return self._request('DELETE', f'/kv/{key}')
    
    def execute_command(self, command):
        """Execute a raw Radish command."""
        return self._request('POST', '/command', {'command': command})


def main():
    """Example usage of the Radish HTTP client."""
    print("=" * 60)
    print("Radish HTTP Client Example ")
    print("=" * 60)
    print()
    
    # Create client
    client = RadishHTTPClient('http://localhost:8000')
    
    # Test 1: Ping
    print("1. Testing server connection...")
    result = client.ping()
    print(f"   {result}")
    print()
    
    # Test 2: Create a cache
    print("2. Creating 'users' cache...")
    result = client.create_cache('users')
    print(f"   {result}")
    print()
    
    # Test 3: Add users
    print("3. Adding users...")
    users = [
        ('user1', 'john@example.com'),
        ('user2', 'jane@example.com'),
        ('user3', 'bob@example.com')
    ]
    for username, email in users:
        result = client.cache_set('users', username, email)
        print(f"   {username}: {result}")
    print()
    
    # Test 4: Get all users
    print("4. Getting all users...")
    result = client.cache_get_all('users')
    print(json.dumps(result, indent=2))
    print()
    
    # Test 5: Get specific user
    print("5. Getting user1...")
    result = client.cache_get('users', 'user1')
    print(f"   {result}")
    print()
    
    # Test 6: List cache keys
    print("6. Listing all keys in users cache...")
    result = client.cache_keys('users')
    print(f"   Keys: {result.get('keys', [])}")
    print()
    
    # Test 7: Create cache with complex data
    print("7. Creating 'products' cache with complex data...")
    client.create_cache('products')
    products = [
        ('laptop', {'name': 'Dell XPS', 'price': 1200, 'inStock': True}),
        ('mouse', {'name': 'Logitech MX', 'price': 80, 'inStock': True}),
        ('keyboard', {'name': 'Mechanical', 'price': 150, 'inStock': False})
    ]
    for product_id, product_data in products:
        result = client.cache_set('products', product_id, product_data)
        print(f"   {product_id}: {result}")
    print()
    
    # Test 8: Get all products
    print("8. Getting all products...")
    result = client.cache_get_all('products')
    print(json.dumps(result, indent=2))
    print()
    
    # Test 9: Delete a user
    print("9. Deleting user2...")
    result = client.cache_delete('users', 'user2')
    print(f"   {result}")
    print()
    
    # Test 10: Check users after deletion
    print("10. Users after deletion:")
    result = client.cache_get_all('users')
    for username, email in result.items():
        print(f"    {username}: {email}")
    print()
    
    # Test 11: Work with main store
    print("11. Working with main key-value store...")
    client.set_value('greeting', 'Hello World!')
    result = client.get_value('greeting')
    print(f"    {result}")
    print()
    
    # Test 12: Execute raw command
    print("12. Executing raw LISTCACHES command...")
    result = client.execute_command('LISTCACHES')
    print(f"    {result.get('response', '')}")
    print()
    
    # Test 13: List all caches
    print("13. Listing all caches...")
    result = client.list_caches()
    print(f"    {result.get('caches', '')}")
    print()
    
    print("=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
