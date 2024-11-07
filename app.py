from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rat Inspection Interface</title>
</head>
<body>
    <h1>Rat</h1>
    <button onclick="location.href='/sighting'">Sighting</button>
    <button onclick="location.href='/report'">Report</button>
    <button onclick="location.href='/qa'">Q&A</button>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_template)

@app.route('/sighting')
def sighting():
    return "Sighting Page (Coming soon)"

@app.route('/report')
def report():
    return "Report Page (Coming soon)"

@app.route('/qa')
def qa():
    return "Q&A Page (Coming soon)"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
