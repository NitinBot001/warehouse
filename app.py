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
    
    files = [
        'static/punjab.csv', 'static/bihar.csv', 'static/haryana.csv', 'static/all.csv',
        'static/andrapradesh.csv', 'static/assam.csv', 'static/chandigarh.csv',
        'static/chhattisgarh.csv', 'static/delhinct.csv', 'static/goa.csv', 'static/gujrat.csv',
        'static/himanchalpradesh.csv', 'static/jharkhand.csv', 'static/jk.csv',
        'static/karnataka.csv', 'static/kerala.csv', 'static/madhyapradesh.csv',
        'static/maharastra.csv', 'static/nagaland.csv', 'static/odisha.csv',
        'static/puducherry.csv', 'static/rajasthan.csv', 'static/tamilnadu.csv',
        'static/telangana.csv', 'static/uttarpradesh.csv', 'static/westbengal.csv'
    ]
    
    data = []
    for file in files:
        if not os.path.exists(file):
            continue
            
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.read().strip().split('\n')
            if not lines:
                continue
            
            # Parse header
            headers = [h.strip() for h in lines[0].split(',')]
            
            # Parse data rows
            for line in lines[1:]:
                if not line.strip():
                    continue
                
                # Split by comma (basic CSV parsing)
                values = line.split(',')
                row = {}
                
                for i, header in enumerate(headers):
                    if i < len(values):
                        row[header] = values[i].strip()
                
                # Convert capacity to int
                try:
                    capacity_val = row.get('Capacity(in MT)', '0').strip()
                    row['Capacity(in MT)'] = int(capacity_val) if capacity_val else 0
                except (ValueError, AttributeError):
                    row['Capacity(in MT)'] = 0
                
                # Pre-compute lowercase for faster filtering
                row['_district_lower'] = row.get('District', '').lower()
                row['_state_lower'] = row.get('State', '').lower()
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
