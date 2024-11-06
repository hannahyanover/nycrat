from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World! This is a simple web server."

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        'message': 'Welcome to the API!',
        'data': [1, 2, 3, 4, 5]
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
