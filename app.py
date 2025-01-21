from flask import Flask, jsonify, request
from azure.cosmos import CosmosClient, exceptions

# Flask app initialization
app = Flask(__name__)

# Cosmos DB connection details
COSMOS_DB_CONNECTION_STRING = "AccountEndpoint=https://my-cosmos-super-db.documents.azure.com:443/;AccountKey=mQPPHiKMMksgrQeC0T5TUJBKxUA6trK2i70MSKSWmwTn95hGYUsXS06SznpZ9koq2bUtBuPCAomQACDbAYKycw==;"
DATABASE_NAME = "ProjectData"
CONTAINER_NAME = "ProjectData"

# Initialize Cosmos Client
cosmos_client = CosmosClient.from_connection_string(COSMOS_DB_CONNECTION_STRING)
database = cosmos_client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

# Root endpoint
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Cargo Humidity Monitoring API!"})

# Get all humidity data
@app.route('/api/humidity', methods=['GET'])
def get_humidity_data():
    try:
        query = "SELECT * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        return jsonify({"humidity_data": items}), 200
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({"error": str(e)}), 500

# Get humidity data for a specific truck
@app.route('/api/humidity/<truck_id>', methods=['GET'])
def get_humidity_for_truck(truck_id):
    try:
        query = f"SELECT * FROM c WHERE c.device_id = '{truck_id}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        if not items:
            return jsonify({"message": "No data found for this truck"}), 404
        return jsonify({"truck_id": truck_id, "humidity_data": items}), 200
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({"error": str(e)}), 500

# Add new humidity data
@app.route('/api/humidity', methods=['POST'])
def add_humidity_data():
    try:
        data = request.json
        if not data or 'device_id' not in data or 'humidity' not in data:
            return jsonify({"error": "Invalid data format"}), 400

        # Add timestamp to the data
        data['timestamp'] = request.json.get('timestamp', None)

        # Insert into Cosmos DB
        container.create_item(body=data)
        return jsonify({"message": "Data added successfully", "data": data}), 201
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({"error": str(e)}), 500

# Delete humidity data for a specific truck
@app.route('/api/humidity/<truck_id>', methods=['DELETE'])
def delete_humidity_data(truck_id):
    try:
        query = f"SELECT * FROM c WHERE c.device_id = '{truck_id}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        if not items:
            return jsonify({"message": "No data found to delete for this truck"}), 404

        for item in items:
            container.delete_item(item=item['id'], partition_key=item['device_id'])

        return jsonify({"message": f"Data for truck {truck_id} deleted successfully"}), 200
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({"error": str(e)}), 500

# Update humidity data for a specific truck
@app.route('/api/humidity/<truck_id>', methods=['PUT'])
def update_humidity_data(truck_id):
    try:
        data = request.json
        if not data or 'humidity' not in data:
            return jsonify({"error": "Invalid data format"}), 400

        query = f"SELECT * FROM c WHERE c.device_id = '{truck_id}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        if not items:
            return jsonify({"message": "No data found to update for this truck"}), 404

        updated_data = []
        for item in items:
            item['humidity'] = data['humidity']
            container.replace_item(item=item['id'], body=item)
            updated_data.append(item)

        return jsonify({"message": "Data updated successfully", "updated_data": updated_data}), 200
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({"error": str(e)}), 500

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
