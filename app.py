from flask import Flask, jsonify, request
from flask_cors import CORS
import csv
import os

app = Flask(__name__)
CORS(app)

def load_warehouse_data():
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
        file = file.strip()
        if not os.path.exists(file):
            print(f"Warning: {file} not found, skipping...")
            continue
        with open(file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row['Capacity(in MT)'] = int(row.get('Capacity(in MT)', '0').strip())
                except (ValueError, AttributeError):
                    row['Capacity(in MT)'] = 0
                row['SourceFile'] = file
                data.append(row)

    return data

@app.route('/warehouses', methods=['GET'])
def get_warehouses():
    district = request.args.get('district')
    state = request.args.get('state')

    data = load_warehouse_data()

    if district:
        data = [w for w in data if w.get('District', '').lower() == district.lower()]
    if state:
        data = [w for w in data if w.get('State', '').lower() == state.lower()]

    if not data:
        return jsonify({'error': 'No warehouses found for the specified district and/or state'}), 404

    return jsonify(data)

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Warehouse API",
        "usage": {
            "/warehouses": "Get all warehouses",
            "/warehouses?district=<district_name>": "Filter by district",
            "/warehouses?state=<state_name>": "Filter by state",
            "/warehouses?district=<district>&state=<state>": "Filter by both"
        }
    })

# For Vercel
def handler(event, context):
    return app(event, context)

if __name__ == '__main__':
    app.run(debug=True)
