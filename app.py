import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, jsonify, render_template_string, flash, session, abort 

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

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

DB_USER = "zz3306"
DB_PASSWORD = "hry2106"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://zz3306:hry2106@w4111.cisxo09blonu.us-east-1.rds.amazonaws.com/w4111"

engine = create_engine(DATABASEURI)

with engine.connect() as connection:
    # Drop the table if it exists
    connection.execute("""DROP TABLE IF EXISTS test;""")
    
    # Create the table if it doesn't exist
    connection.execute("""CREATE TABLE IF NOT EXISTS test (
        id serial PRIMARY KEY,
        name text
    );""")
    
    # Insert values into the table
    connection.execute("""INSERT INTO test(name) VALUES 
        ('grace hopper'), 
        ('alan turing'), 
        ('ada lovelace');""")

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


@app.route('/')
def home():
    # if not session.get('logged_in'):
    #     return render_template('login.html')
    # else:
        return render_template_string(html_template)

# @app.route('/login', methods=['POST'])
# def do_admin_login():
#     if request.form['password'] == 'password' and request.form['username'] == 'admin':
#         session['logged_in'] = True
#     else:
#         flash('wrong password!')
#     return home()

@app.route('/sighting')
def sighting():
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = names)
  return render_template("index.html", **context)

 

@app.route('/report')
def report():
    return "Inspection Posts Page (Coming soon)"

@app.route('/qa')
def qa():
    return "Q&A Forum (Coming soon)"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
