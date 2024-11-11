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

with engine.connect() as connection:  # "with" ensures the connection is properly closed

    connection.execute(text("DROP TABLE IF EXISTS Email CASCADE;"))
    connection.execute(text("""
        CREATE TABLE Email (
            email_address TEXT,
            name TEXT,
            PRIMARY KEY (email_address)
        );
    """))

    connection.execute(text("DELETE FROM Email;"))
    connection.execute(text("INSERT INTO Email VALUES ('hry2106@columbia.edu','HannahYanover');"))
    connection.execute(text("INSERT INTO Email VALUES ('zz3306@columbia.edu','LucasZheng');"))
    connection.execute(text("INSERT INTO Email VALUES ('abc1234@columbia.edu', 'AliceBrown');"))
    connection.execute(text("INSERT INTO Email VALUES ('def5678@columbia.edu', 'DavidSmith');"))
    connection.execute(text("INSERT INTO Email VALUES ('ghi9012@columbia.edu', 'EmilyJohnson');"))
    connection.execute(text("INSERT INTO Email VALUES ('jkl3456@columbia.edu', 'MichaelLee');"))
    connection.execute(text("INSERT INTO Email VALUES ('mno7890@columbia.edu', 'SophiaMartinez');"))
    connection.execute(text("INSERT INTO Email VALUES ('pqr1234@columbia.edu', 'JamesTaylor');"))
    connection.execute(text("INSERT INTO Email VALUES ('stu5678@columbia.edu', 'OliviaWilliams');"))
    connection.execute(text("INSERT INTO Email VALUES ('vwx9012@columbia.edu', 'WilliamClark');"))


    connection.execute(text("""DROP TABLE IF EXISTS personal_rat_sighting CASCADE;"""))
    connection.execute(text("""DROP TABLE IF EXISTS inspection_post CASCADE;"""))
    connection.execute(text("""DROP TABLE IF EXISTS post CASCADE;"""))
    
    connection.execute(text("""CREATE TABLE personal_rat_sighting (
        sighting_id int PRIMARY KEY,
        zip_code int,
        comment text
    );"""))

    connection.execute(text("""CREATE TABLE inspection_post (
        job_id text PRIMARY KEY,
        zip_code int,
        borough text,
        result text,
        date date
    );"""))

    connection.execute(text("""CREATE TABLE post (
        post_id int PRIMARY KEY,
        sighting_id int REFERENCES personal_rat_sighting,
        job_id text REFERENCES inspection_post,
        CHECK ((sighting_id IS NULL OR job_id IS NULL) AND (sighting_id IS NOT NULL OR job_id IS NOT NULL))
    );"""))
    
    connection.execute(text("DELETE FROM personal_rat_sighting;"))
    connection.execute(text("""INSERT INTO personal_rat_sighting VALUES(1, 10458, 'Saw a rat near Fordham Road in the Bronx.');"""))  # Zip code 10458 (Bronx)
    connection.execute(text("""INSERT INTO personal_rat_sighting VALUES(2, 10022, 'Spotted a rat near Grand Central Terminal in Midtown Manhattan.');"""))  # Zip code 10022 (Midtown Manhattan)
    connection.execute(text("""INSERT INTO personal_rat_sighting VALUES(3, 11206, 'Spotted a rat in the Bushwick area of Brooklyn.');"""))  # Zip code 11206 (Bushwick, Brooklyn)
    connection.execute(text("""INSERT INTO personal_rat_sighting VALUES(4, 10032, 'Saw a rat near the medical campus in Washington Heights.');"""))  # Zip code 10032 (Washington Heights)
    connection.execute(text("""INSERT INTO personal_rat_sighting VALUES(5, 10457, 'A rat ran across the street in the Kingsbridge area of the Bronx.');"""))  # Zip code 10457 (Kingsbridge, Bronx)
    connection.execute(text("""INSERT INTO personal_rat_sighting VALUES(6, 11237, 'Witnessed a rat in the residential area of Ridgewood, Queens.');"""))  # Zip code 11237 (Ridgewood, Queens)
    connection.execute(text("""INSERT INTO personal_rat_sighting VALUES(7, 11385, 'Saw a rat near Wyckoff Avenue in Ridgewood.');"""))  # Zip code 11385 (Ridgewood, Queens)
    connection.execute(text("""INSERT INTO personal_rat_sighting VALUES(8, 10458, 'A rat crossed the street near the Bronx Zoo.');"""))  # Zip code 10458 (Bronx Zoo area)
    connection.execute(text("""INSERT INTO personal_rat_sighting VALUES(9, 10453, 'Saw a rat near 170th Street in the Bronx.');"""))  # Zip code 10453 (Bronx)
    connection.execute(text("""INSERT INTO personal_rat_sighting VALUES(10, 11219, 'Spotted a rat near the Sunset Park area of Brooklyn.');"""))  # Zip code 11219 (Sunset Park, Brooklyn)

    connection.execute(text("DELETE FROM inspection_post;"))
    connection.execute(text("""INSERT INTO inspection_post (job_id, zip_code, borough, result, date)
                               VALUES ('PC6530234', 10458, 'Bronx', 'Passed', '2010-08-30 15:23:11')"""))

    connection.execute(text("""INSERT INTO inspection_post (job_id, zip_code, borough, result, date)
                               VALUES ('PC6101553', 10022, 'Manhattan', 'Passed', '2011-08-18 12:05:54')"""))

    connection.execute(text("""INSERT INTO inspection_post (job_id, zip_code, borough, result, date)
                               VALUES ('PC7270050', 11206, 'Brooklyn', 'Passed', '2018-10-10 12:57:02')"""))

    connection.execute(text("""INSERT INTO inspection_post (job_id, zip_code, borough, result, date)
                               VALUES ('PC6481130', 10032, 'Manhattan', 'Passed', '2019-02-07 12:48:34')"""))

    connection.execute(text("""INSERT INTO inspection_post (job_id, zip_code, borough, result, date)
                               VALUES ('PC6794074', 10457, 'Bronx', 'Rat Activity', '2017-10-16 13:02:51')"""))

    connection.execute(text("""INSERT INTO inspection_post (job_id, zip_code, borough, result, date)
                               VALUES ('PC7229376', 11237, 'Brooklyn', 'Passed', '2019-06-20 16:02:23')"""))

    connection.execute(text("""INSERT INTO inspection_post (job_id, zip_code, borough, result, date)
                               VALUES ('PC7376230', 11385, 'Queens', 'Bait applied', '2017-08-01 09:45:13')"""))

    connection.execute(text("""INSERT INTO inspection_post (job_id, zip_code, borough, result, date)
                               VALUES ('PC7552325', 10458, 'Bronx', 'Passed', '2013-07-18 15:46:40')"""))

    connection.execute(text("""INSERT INTO inspection_post (job_id, zip_code, borough, result, date)
                               VALUES ('PC6543128', 10453, 'Bronx', 'Rat Activity', '2012-01-25 14:45:24')"""))

    connection.execute(text("""INSERT INTO inspection_post (job_id, zip_code, borough, result, date)
                               VALUES ('PC6986296', 11219, 'Brooklyn', 'Failed for Other', '2010-09-28 10:25:40')"""))

    connection.execute(text("DELETE FROM post;"))
    # Example for inserting data into the 'post' table
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (1, 1, NULL)"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (2, 2, NULL)"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (3, 3, NULL)"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (4, 4, NULL)"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (5, 5, NULL)"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (6, 6, NULL)"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (7, 7, NULL)"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (8, 8, NULL)"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (9, 9, NULL)"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (10, 10, NULL)"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (11, NULL, 'PC6530234')"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (12, NULL, 'PC6101553')"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (13, NULL, 'PC7270050')"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (14, NULL, 'PC6481130')"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (15, NULL, 'PC6794074')"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (16, NULL, 'PC7229376')"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (17, NULL, 'PC7376230')"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (18, NULL, 'PC7552325')"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (19, NULL, 'PC6543128')"""))
    
    connection.execute(text("""INSERT INTO post (post_id, sighting_id, job_id) 
                               VALUES (20, NULL, 'PC6986296')"""))

    connection.execute(text("DROP TABLE IF EXISTS Personal_rat_sighting_Share;"))
    connection.execute(text("""
        CREATE TABLE Personal_rat_sighting_Share(
          sighting_id INT,
          zip_code INT,
          comment TEXT,
          email_address TEXT,
          PRIMARY KEY (sighting_id, email_address),
          FOREIGN KEY (email_address) REFERENCES Email
          ON DELETE CASCADE
        );
    """))
    connection.execute(text("DELETE FROM Personal_rat_sighting_Share;"))
    connection.execute(text("INSERT INTO Personal_rat_sighting_Share VALUES(1, 10458, 'Saw a rat near Fordham Road in the Bronx.', 'hry2106@columbia.edu');"))
    connection.execute(text("INSERT INTO Personal_rat_sighting_Share VALUES(2, 10022, 'Spotted a rat near Grand Central Terminal in Midtown Manhattan.', 'zz3306@columbia.edu');"))
    connection.execute(text("INSERT INTO Personal_rat_sighting_Share VALUES(3, 11206, 'Spotted a rat in the Bushwick area of Brooklyn.', 'abc1234@columbia.edu');"))
    connection.execute(text("INSERT INTO Personal_rat_sighting_Share VALUES(4, 10032, 'Saw a rat near the medical campus in Washington Heights.', 'def5678@columbia.edu');"))
    connection.execute(text("INSERT INTO Personal_rat_sighting_Share VALUES(5, 10457, 'A rat ran across the street in the Kingsbridge area of the Bronx.', 'ghi9012@columbia.edu');"))
    connection.execute(text("INSERT INTO Personal_rat_sighting_Share VALUES(6, 11237, 'Witnessed a rat in the residential area of Ridgewood, Queens.', 'jkl3456@columbia.edu');"))
    connection.execute(text("INSERT INTO Personal_rat_sighting_Share VALUES(7, 11385, 'Saw a rat near Wyckoff Avenue in Ridgewood.', 'mno7890@columbia.edu');"))
    connection.execute(text("INSERT INTO Personal_rat_sighting_Share VALUES(8, 10458, 'A rat crossed the street near the Bronx Zoo.', 'pqr1234@columbia.edu');"))
    connection.execute(text("INSERT INTO Personal_rat_sighting_Share VALUES(9, 10453, 'Saw a rat near 170th Street in the Bronx.', 'stu5678@columbia.edu');"))
    connection.execute(text("INSERT INTO Personal_rat_sighting_Share VALUES(10, 11219, 'Spotted a rat near the Sunset Park area of Brooklyn.', 'vwx9012@columbia.edu');"))

    connection.execute(text("DROP TABLE IF EXISTS Vote;"))
    connection.execute(text("""
        CREATE TABLE Vote(
          email_address TEXT REFERENCES Email,
          post_id INT REFERENCES Post,
          up_down BOOLEAN,
          PRIMARY KEY(email_address, post_id)
        );
    """))
    connection.execute(text("DELETE FROM Vote;"))
    connection.execute(text("INSERT INTO Vote VALUES('zz3306@columbia.edu', 1, FALSE);"))
    connection.execute(text("INSERT INTO Vote VALUES('ghi9012@columbia.edu', 2, TRUE);"))
    connection.execute(text("INSERT INTO Vote VALUES('hry2106@columbia.edu', 3, FALSE);"))
    connection.execute(text("INSERT INTO Vote VALUES('mno7890@columbia.edu', 4, TRUE);"))
    connection.execute(text("INSERT INTO Vote VALUES('abc1234@columbia.edu', 5, FALSE);"))
    connection.execute(text("INSERT INTO Vote VALUES('pqr1234@columbia.edu', 6, TRUE);"))
    connection.execute(text("INSERT INTO Vote VALUES('stu5678@columbia.edu', 7, FALSE);"))
    connection.execute(text("INSERT INTO Vote VALUES('vwx9012@columbia.edu', 8, TRUE);"))
    connection.execute(text("INSERT INTO Vote VALUES('jkl3456@columbia.edu', 9, FALSE);"))
    connection.execute(text("INSERT INTO Vote VALUES('def5678@columbia.edu', 10, TRUE);"))

    connection.execute(text("DROP TABLE IF EXISTS comment_on;"))
    connection.execute(text("""
        CREATE TABLE comment_on(
          on_id SERIAL,
          text TEXT,
          post_id INT NOT NULL,
          PRIMARY KEY (on_id),
          FOREIGN KEY (post_id) REFERENCES Post
            ON DELETE CASCADE
        );
    """))
    connection.execute(text("DELETE FROM comment_on;"))
    connection.execute(text("INSERT INTO comment_on VALUES (1, 'omg me too!', 1);"))
    connection.execute(text("INSERT INTO comment_on VALUES (2, 'really?!', 2);"))
    connection.execute(text("INSERT INTO comment_on VALUES (3, 'not surprising', 3);"))
    connection.execute(text("INSERT INTO comment_on VALUES (4, 'cannot believe this', 4);"))
    connection.execute(text("INSERT INTO comment_on VALUES (5, 'did it run or did it scuttle though', 5);"))
    connection.execute(text("INSERT INTO comment_on VALUES (6, 'wow the Bronx passed', 11);"))
    connection.execute(text("INSERT INTO comment_on VALUES (7, 'this zipcode never has rats', 12);"))
    connection.execute(text("INSERT INTO comment_on VALUES (8, 'this zipcode always has rats', 13);"))
    connection.execute(text("INSERT INTO comment_on VALUES (9, 'they should not have passed', 14);"))
    connection.execute(text("INSERT INTO comment_on VALUES (10, 'there definitely is rat activity!', 15);"))


    connection.execute(text("DROP TABLE IF EXISTS comment_write;"))
    connection.execute(text("""
        CREATE TABLE comment_write(
          write_id SERIAL,
          text TEXT,
          email_address TEXT NOT NULL,
          PRIMARY KEY (write_id),
          FOREIGN KEY (email_address) REFERENCES Email
            ON DELETE CASCADE
        );
    """))

    connection.execute(text("DELETE FROM comment_write;"))
    connection.execute(text("INSERT INTO comment_write VALUES (1, 'omg me too!', 'ghi9012@columbia.edu');"))
    connection.execute(text("INSERT INTO comment_write VALUES (2, 'really?!', 'abc1234@columbia.edu');"))
    connection.execute(text("INSERT INTO comment_write VALUES (3, 'not surprising', 'hry2106@columbia.edu');"))
    connection.execute(text("INSERT INTO comment_write VALUES (4, 'cannot believe this', 'vwx9012@columbia.edu');"))
    connection.execute(text("INSERT INTO comment_write VALUES (5, 'did it run or did it scuttle though', 'stu5678@columbia.edu');"))
    connection.execute(text("INSERT INTO comment_write VALUES (6, 'wow the Bronx passed', 'zz3306@columbia.edu');"))
    connection.execute(text("INSERT INTO comment_write VALUES (7, 'this zipcode never has rats', 'pqr1234@columbia.edu');"))
    connection.execute(text("INSERT INTO comment_write VALUES (8, 'this zipcode always has rats', 'mno7890@columbia.edu');"))
    connection.execute(text("INSERT INTO comment_write VALUES (9, 'they should not have passed', 'jkl3456@columbia.edu');"))
    connection.execute(text("INSERT INTO comment_write VALUES (10, 'there definitely is rat activity!', 'def5678@columbia.edu');"))
    
    connection.commit()

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
                co.text AS comment_text
            FROM 
                personal_rat_sighting AS prs
            JOIN 
                post AS p ON prs.sighting_id = p.sighting_id
            LEFT JOIN 
                comment_on AS co ON p.post_id = co.post_id
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

@app.route('/report')
def report():
    engine = create_engine(DATABASEURI)
    with engine.connect() as connection:  # "with" ensures the connection is properly closed after use
        result = connection.execute(text("""
            SELECT 
                prs.sighting_id,
                prs.zip_code,
                prs.comment AS sighting_comment,
                co.text AS comment_text,
                COALESCE(SUM(CASE WHEN v.vote = TRUE THEN 1 WHEN v.vote = FALSE THEN -1 ELSE 0 END), 0) AS like_count
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

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0', port=5000)
