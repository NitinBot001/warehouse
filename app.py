from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Cache data in memory on startup
WAREHOUSE_DATA = None

def load_warehouse_data():
    """Load all CSV files once using manual parsing (no csv module)"""
    global WAREHOUSE_DATA
    
    if WAREHOUSE_DATA is not None:
        return WAREHOUSE_DATA
    
    files = [ 'static/all.csv']
    
    data = []
    for file in files:
        if not os.path.exists(file):
            continue
            
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.read().strip().split('\n')
            if not lines:
                continue
            
            # Parse header - remove quotes and strip
            headers = [h.strip().strip('"').strip("'") for h in lines[0].split(',')]
            
            # Parse data rows
            for line in lines[1:]:
                if not line.strip():
                    continue
                
                # Split by comma and handle quotes
                values = []
                current = ''
                in_quotes = False
                
                for char in line:
                    if char in ('"', "'"):
                        in_quotes = not in_quotes
                    elif char == ',' and not in_quotes:
                        values.append(current.strip())
                        current = ''
                    else:
                        current += char
                values.append(current.strip())
                
                row = {}
                for i, header in enumerate(headers):
                    if i < len(values):
                        row[header] = values[i].strip('"').strip("'").strip()
                
                # Convert capacity to int
                try:
                    capacity_val = row.get('Capacity(in MT)', '0').strip()
                    row['Capacity(in MT)'] = int(capacity_val) if capacity_val else 0
                except (ValueError, AttributeError):
                    row['Capacity(in MT)'] = 0
                
                # Pre-compute lowercase for faster filtering
                row['_district_lower'] = row.get('District', '').lower().strip()
                row['_state_lower'] = row.get('State', '').lower().strip()
                data.append(row)
    
    WAREHOUSE_DATA = data
    return data

@app.route('/warehouses', methods=['GET'])
def get_warehouses():
    district = request.args.get('district', '').lower()
    state = request.args.get('state', '').lower()
    
    data = load_warehouse_data()
    
    # Filter efficiently
    if district and state:
        filtered = [w for w in data if w['_district_lower'] == district and w['_state_lower'] == state]
    elif district:
        filtered = [w for w in data if w['_district_lower'] == district]
    elif state:
        filtered = [w for w in data if w['_state_lower'] == state]
    else:
        filtered = data
    
    if not filtered:
        return jsonify({'error': 'No warehouses found'}), 404
    
    # Remove internal fields before returning
    result = [{k: v for k, v in w.items() if not k.startswith('_')} for w in filtered]
    
    return jsonify(result)

# Add this temporary route to see your data
@app.route('/debug')
def debug():
    data = load_warehouse_data()
    if data:
        return jsonify({
            "total_records": len(data),
            "sample_record": data[0],
            "all_keys": list(data[0].keys())
        })
    return jsonify({"error": "No data loaded"})

@app.route('/')
def home():
    return jsonify({
        "message": "Warehouse API",
        "endpoints": {
            "/warehouses": "Get all warehouses",
            "/warehouses?district=name": "Filter by district",
            "/warehouses?state=name": "Filter by state"
        }
    })

# Load data once at startup
with app.app_context():
    load_warehouse_data()

if __name__ == '__main__':
    app.run(debug=False, port=10000, host='0.0.0.0')
