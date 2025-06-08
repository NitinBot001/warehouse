import http.server
import socketserver
import json
import csv
from urllib.parse import parse_qs, urlparse

# Defining the port for the server
PORT = 8000

# Loading and parsing CSV data from multiple state files
def load_warehouse_data():
    files = ['/static/punjab.csv', '/static/bihar.csv', '/static/haryana.csv', '/static/all.csv ', '/static/andrapradesh.csv ', '/static/assam.csv ', '/static/chandigarh.csv ', '/static/chhattisgarh.csv ', '/static/delhinct.csv ', '/static/goa.csv ', '/static/gujrat.csv ', '/static/himanchalpradesh.csv ', '/static/jharkhand.csv ', '/static/jk.csv ', '/static/karnataka.csv ', '/static/kerala.csv ', '/static/madhyapradesh.csv ', '/static/maharastra.csv ', '/static/nagaland.csv ', '/static/odisha.csv ', '/static/puducherry.csv ', '/static/rajasthan.csv ', '/static/tamilnadu.csv ', '/static/telangana.csv ', '/static/uttarpradesh.csv ', '/static/westbengal.csv']
    data = []
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Cleaning and converting capacity to integer
                    try:
                        row['Capacity(in MT)'] = int(row['Capacity(in MT)'].strip())
                    except (ValueError, AttributeError):
                        row['Capacity(in MT)'] = 0
                    # Adding source file info for state context
                    row['SourceFile'] = file
                    data.append(row)
        except FileNotFoundError:
            print(f"Warning: {file} not found, skipping...")
    return data

# Creating a custom request handler
class WarehouseRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Adding CORS headers to allow requests from any origin
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        # Handling preflight OPTIONS request for CORS
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        # Parsing the URL and query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # Loading warehouse data
        warehouse_data = load_warehouse_data()
        
        # Handling the /warehouses endpoint with district and state filters
        if parsed_url.path == '/warehouses':
            district = query_params.get('district', [None])[0]
            state = query_params.get('state', [None])[0]
            
            # Applying filters
            filtered_data = warehouse_data
            if district:
                filtered_data = [w for w in filtered_data if w['District'].lower() == district.lower()]
            if state:
                filtered_data = [w for w in filtered_data if w['State'].lower() == state.lower()]
            
            if filtered_data:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(filtered_data).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'No warehouses found for the specified district and/or state'}).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode('utf-8'))

# Setting up and starting the server
def run_server():
    server_address = ('', PORT)
    httpd = socketserver.TCPServer(server_address, WarehouseRequestHandler)
    print(f"Server running on port {PORT}")
    print("Available endpoints:")
    print("- GET /warehouses : Get all warehouses")
    print("- GET /warehouses?district=<district_name> : Filter warehouses by district")
    print("- GET /warehouses?state=<state_name> : Filter warehouses by state")
    print("- GET /warehouses?district=<district_name>&state=<state_name> : Filter by both district and state")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print("Server stopped")

# Running the server
if __name__ == '__main__':
    run_server()
