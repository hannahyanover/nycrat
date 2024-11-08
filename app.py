from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rat</title>
    <style>
        body {
            text-align: center;
            font-family: Arial, sans-serif;
        }
        h1 {
            font-size: 3em;
            margin-top: 20px;
        }
        button {
            font-size: 1.2em;
            margin: 10px;
            padding: 10px 20px;
        }
        .rat-image {
            width: 80%;
            max-width: 600px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Lucas and Hannah's Rat Sighting Website</h1>
    <button onclick="location.href='/sighting'">Personal Rat Sighting</button>
    <button onclick="location.href='/report'">Inspection Posts</button>
    <button onclick="location.href='/qa'">Q&A Forum</button>
    <br>
    <img src="https://cdn.theatlantic.com/thumbor/ILSffj75k48V6kniK1TJMh1DXAw=/0x0:2400x3000/648x810/media/img/2023/03/01/Rats_opener4x5-1/original.jpg" alt="Rat in NYC" class="rat-image">
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_template)

@app.route('/sighting')
def sighting():
    return "Personal Rat Sighting Page (Coming soon)"

@app.route('/report')
def report():
    return "Inspection Posts Page (Coming soon)"

@app.route('/qa')
def qa():
    return "Q&A Forum (Coming soon)"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
