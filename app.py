import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, jsonify, render_template_string, flash, session, abort

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DB_USER = "zz3306"
DB_PASSWORD = "hry2106"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://zz3306:hry2106@w4111.cisxo09blonu.us-east-1.rds.amazonaws.com/w4111"

engine = create_engine(DATABASEURI)

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
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('home.html')

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()

@app.route('/sighting')
def sighting():
    engine = create_engine(DATABASEURI)
    with engine.connect() as connection:  # "with" ensures the connection is properly closed after use
        result = connection.execute(text("""
             SELECT 
                prs.sighting_id,
                prs.zip_code,
                prs.comment AS sighting_comment,
                co.text AS comment_text,
                COALESCE(SUM(CASE WHEN v.up_down = TRUE THEN 1 WHEN v.up_down = FALSE THEN -1 ELSE 0 END), 0) AS like_count
            FROM 
                personal_rat_sighting AS prs
            JOIN 
                post AS p ON prs.sighting_id = p.sighting_id
            LEFT JOIN 
                comment_on AS co ON p.post_id = co.post_id
            LEFT JOIN 
                Vote AS v ON p.post_id = v.post_id
            GROUP BY 
                prs.sighting_id, prs.zip_code, prs.comment, co.text
            ORDER BY 
                prs.sighting_id;
        """))
        
        columns = result.keys()  # Get column names (headers)
        formatted_result = [dict(zip(columns, row)) for row in result.fetchall()]
    
    return render_template("personal_sighting.html", data=formatted_result)

@app.route('/search_sighting', methods=['POST'])
def search_sighting():
    # Get the name from the form submission
    zip_code = request.form['zip_code']

    try:
        zip_code = int(request.form['zip_code'])  # Converts input to integer if possible
    except ValueError:
        # If conversion fails, redirect or render an error message
        return render_template("personal_sighting.html", data=[])
    
    engine = create_engine(DATABASEURI)
    with engine.connect() as connection:  # "with" ensures the connection is properly closed after use
         query = text("SELECT * FROM personal_rat_sighting WHERE zip_code = :zip_code")
         result = connection.execute(query, {"zip_code": zip_code})
         columns = result.keys()  # Get column names (headers)
         formatted_result = [dict(zip(columns, row)) for row in result.fetchall()]
    return render_template("personal_sighting.html", data=formatted_result)


@app.route('/update_like', methods=['POST'])
def update_like():
    data = request.get_json()
    post_id = data['post_id']
    action = data['action']
    email_address = 'admin'  # Assuming user email is stored in session

    # Determine the 'up_down' value for the vote
    up_down = True if action == 'add' else False  # 1 for like, -1 for dislike

    # Check if the user has already voted
    engine = create_engine(DATABASEURI)
    with engine.connect() as connection:
        # Check if the user already voted for this post
        result = connection.execute(text("""
            SELECT up_down 
            FROM Vote 
            WHERE post_id = :post_id AND email_address = :email_address
        """), {'post_id': post_id, 'email_address': email_address})
        
        current_vote = result.fetchone()
        
        if current_vote:
            # If a vote already exists, we need to update it
            if current_vote[0] != up_down:
                connection.execute(text("""
                    UPDATE Vote
                    SET up_down = :up_down
                    WHERE post_id = :post_id AND email_address = :email_address
                """), {'post_id': post_id, 'email_address': email_address, 'up_down': up_down})
        else:
            # If no vote exists, insert a new one
            connection.execute(text("""
                INSERT INTO Vote (email_address, post_id, up_down)
                VALUES (:email_address, :post_id, :up_down)
            """), {'email_address': email_address, 'post_id': post_id, 'up_down': up_down})

        # After updating the vote, get the new like count
        result = connection.execute(text("""
            SELECT 
                COALESCE(SUM(CASE WHEN v.up_down = TRUE THEN 1 WHEN v.up_down = FALSE THEN -1 ELSE 0 END), 0) AS like_count
            FROM 
                Vote AS v
            WHERE v.post_id = :post_id
        """), {'post_id': post_id})

        new_like_count = result.scalar()

    return jsonify({'new_like_count': new_like_count})


@app.route('/report')
def report():
    engine = create_engine(DATABASEURI)
    with engine.connect() as connection:  # "with" ensures the connection is properly closed after use
        result = connection.execute(text("""
           SELECT 
                i.job_id, 
                i.zip_code, 
                i.borough, 
                i.result, 
                i.date,
                co.text as comment_text   
            FROM 
                inspection_post AS i
            JOIN 
                post AS p ON i.job_id = p.job_id
            LEFT JOIN 
                comment_on AS co ON p.post_id = co.post_id
        """))
        
        columns = result.keys()  # Get column names (headers)
        formatted_result = [dict(zip(columns, row)) for row in result.fetchall()]
    
    return render_template("inspection_post.html", data=formatted_result)

@app.route('/search_inspection', methods=['POST'])
def search_inspection():
    search = request.form['search']
    engine = create_engine(DATABASEURI)
    
    with engine.connect() as connection:
        try:
            # Try to convert the search input to an integer (for zip code search)
            search_int = int(search)
            query = text("""
                SELECT * FROM inspection_post
                WHERE zip_code = :search_query
            """)
            result = connection.execute(query, {"search_query": search_int})
        
        except ValueError:
            # If the input is not an integer, check if it's one of the boroughs
            boroughs = ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island']
            
            if search in boroughs:
                query = text("""
                    SELECT * FROM inspection_post
                    WHERE borough = :search_query
                """)
                result = connection.execute(query, {"search_query": search})
            else:
                # If input is neither an integer nor a valid borough, return no results or handle error
                return render_template("inspection_post.html", data=[])
        
        # Process and display results
        columns = result.keys()
        formatted_result = [dict(zip(columns, row)) for row in result.fetchall()]
    
    return render_template("inspection_post.html", data=formatted_result)
        

@app.route('/qa')
def qa():
    return "Q&A Forum (Coming soon)"

if __name__ == "__main__":
  import click

  app.secret_key = os.urandom(12)

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
