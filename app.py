import os
from datetime import datetime
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, jsonify, render_template_string, flash, session, abort

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DB_USER = "hry2106"
DB_PASSWORD = "getsmart"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://hry2106:getsmart@w4111.cisxo09blonu.us-east-1.rds.amazonaws.com/w4111"


engine = create_engine(DATABASEURI, connect_args={'connect_timeout': 5})

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
    # testing = g.conn.execute(text("SELECT * FROM test"))
    # print(testing.fetchall())
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
        result = g.conn.execute(text("""
             SELECT 
                prs.sighting_id,
                prs.zip_code,
                prs.comment AS sighting_comment,
                co.text AS comment,
                p.post_id as post_id, 
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
                prs.sighting_id, prs.zip_code, prs.comment, co.text, p.post_id
            ORDER BY 
                prs.sighting_id;
        """))
        # print(result.fetchall)

        columns = result.keys()
        # rows = result.fetchall()
        rows = result.mappings() 

        # test = g.conn.execute(text("SELECT * FROM personal_rat_sighting")).fetchall()
        # print(test)
    
    # Now, we need to format this result into a list of posts, each with its own comments
        formatted_result = []
        current_post = None
        
        for row in rows:
            sighting_id = row['sighting_id']  # Accessing by column name works now
            if current_post is None or current_post['sighting_id'] != sighting_id:
                if current_post:
                    formatted_result.append(current_post)
                current_post = {
                    'sighting_id': sighting_id,
                    'zip_code': row['zip_code'],
                    'sighting_comment': row['sighting_comment'],
                    'like_count': row['like_count'],
                    'post_id': row['post_id'], 
                
                    'comments': []
                }
            if row['comment']:  # If there is a comment for this row
                current_post['comments'].append({'comment_text': row['comment']})

        if current_post:
            formatted_result.append(current_post)
    
        return render_template("personal_sighting.html", data=formatted_result)

        
        # columns = result.keys()  
        # formatted_result = [dict(zip(columns, row)) for row in result.fetchall()]
    
        # return render_template("personal_sighting.html", data=formatted_result)

@app.route('/search_sighting', methods=['POST'])
def search_sighting():
    zip_code = request.form['zip_code']

    try:
        zip_code = int(request.form['zip_code'])  # Converts input to integer if possible
    except ValueError:
        return render_template("personal_sighting.html", data=[])
    
    query = text("""
        SELECT 
                prs.sighting_id,
                prs.zip_code,
                prs.comment AS sighting_comment,
                co.text AS comment,
                p.post_id as post_id, 
                COALESCE(SUM(CASE WHEN v.up_down = TRUE THEN 1 WHEN v.up_down = FALSE THEN -1 ELSE 0 END), 0) AS like_count 
        FROM 
                personal_rat_sighting AS prs
        JOIN 
                post AS p ON prs.sighting_id = p.sighting_id
        LEFT JOIN 
                comment_on AS co ON p.post_id = co.post_id
        LEFT JOIN 
                Vote AS v ON p.post_id = v.post_id
        WHERE zip_code = :zip_code
        GROUP BY 
                prs.sighting_id, prs.zip_code, prs.comment, co.text, p.post_id
        ORDER BY 
                prs.sighting_id;
        """)
    result = g.conn.execute(query, {"zip_code": zip_code})
    columns = result.keys() 
    rows = result.mappings() 
    
    # Now, we need to format this result into a list of posts, each with its own comments
    formatted_result = []
    current_post = None
        
    for row in rows:
            sighting_id = row['sighting_id']  # Accessing by column name works now
            if current_post is None or current_post['sighting_id'] != sighting_id:
                if current_post:
                    formatted_result.append(current_post)
                current_post = {
                    'sighting_id': sighting_id,
                    'zip_code': row['zip_code'],
                    'sighting_comment': row['sighting_comment'],
                    'like_count': row['like_count'],
                    'post_id': row['post_id'], 
                    'comments': []
                }
            if row['comment']:  # If there is a comment for this row
                current_post['comments'].append({'comment_text': row['comment']})

    if current_post:
            formatted_result.append(current_post)
    
    return render_template("personal_sighting.html", data=formatted_result)
    # formatted_result = [dict(zip(columns, row)) for row in result.fetchall()]
    # return render_template("personal_sighting.html", data=formatted_result)


@app.route('/update_like', methods=['POST'])
def update_like():
    print("update like in .py")
    data = request.get_json()
    post_id = data['post_id']
    action = data['action']
    email_address = 'admin'  
    
    up_down = True if action == 'add' else False  
    
    result = g.conn.execute(text("""
            SELECT up_down 
            FROM Vote 
            WHERE post_id = :post_id AND email_address = :email_address
        """), {'post_id': post_id, 'email_address': email_address})
        
    current_vote = result.fetchone()
        
    if current_vote:
            if current_vote[0] != up_down:
                g.conn.execute(text("""
                    UPDATE Vote
                    SET up_down = :up_down
                    WHERE post_id = :post_id AND email_address = :email_address
                """), {'post_id': post_id, 'email_address': email_address
                       , 'up_down': up_down})
    else:
            g.conn.execute(text("""
                INSERT INTO Vote (email_address, post_id, up_down)
                VALUES (:email_address, :post_id, :up_down)
            """), {'email_address': email_address, 'post_id': post_id, 'up_down': up_down})
    result2 = g.conn.execute(text("""
            SELECT 
                COALESCE(SUM(CASE WHEN v.up_down = TRUE THEN 1 WHEN v.up_down = FALSE THEN -1 ELSE 0 END), 0) AS like_count
            FROM 
                Vote AS v
            WHERE v.post_id = :post_id
        """), {'post_id': post_id})
    
    g.conn.commit(); 

    new_like_count = result2.scalar()
    

    return jsonify({'new_like_count': new_like_count})

@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    data = request.json
    post_id = data.get('post_id')
    comment_text = data.get('comment_text')
    
    result = g.conn.execute(text("""
        SELECT * FROM post WHERE post_id = :post_id
    """), {"post_id": post_id})

    post = result.fetchone()
    if not post:
        return jsonify({"error": "Post not found"}), 404

    g.conn.execute(text("""
        INSERT INTO comment_on (text, post_id)
        VALUES (:comment_text, :post_id) 
    """), {"post_id": post_id, "comment_text": comment_text})
    g.conn.commit()

    return jsonify({"message": "Comment added successfully"})

@app.route('/add_sighting', methods=['POST'])
def add_sighting():
        test = g.conn.execute(text("SELECT * FROM personal_rat_sighting")).fetchall()
        print(test)
        # Get user input
        data = request.get_json()
        zip_code2 = data['zip_code']
        try:
            zip_code = int(zip_code2)
            if len(zip_code2)!= 5 :
                return jsonify({'error': 'Invalid zip code'}), 400
        except: 
            return jsonify({'error': 'Invalid zip code'}), 400
            
        comment = data['sighting_comment']
        result = g.conn.execute(text("SELECT MAX(sighting_id) FROM personal_rat_sighting"))
        max_sighting_id = result.fetchone()[0]
        print(max_sighting_id)
        
        if max_sighting_id is None:
            sighting_id = 1
        else:
            sighting_id = max_sighting_id + 1


        job_id = None
        result2 = g.conn.execute(text("SELECT MAX(post_id) FROM post"))
        max_post_id = result2.fetchone()[0]
        print(max_post_id)
        print(zip_code, sighting_id, comment)


        if max_post_id is None:
            post_id = 1
        else:
            post_id = max_post_id + 1

        # Validate input (basic example)
        print("zip code again: ", zip_code, type(zip_code))
        # SQL Query to insert data
        query = text("""
                INSERT INTO personal_rat_sighting (sighting_id, zip_code, comment)
                VALUES (:sighting_id, :zip_code, :comment)
        """)
        g.conn.execute(query, {'sighting_id': sighting_id, 'zip_code': zip_code, 'comment': comment})
        query2 = text("""
                INSERT INTO post (post_id, sighting_id, job_id)
                VALUES (:post_id, :sighting_id, :job_id)
        """)
        g.conn.execute(query2, {'post_id': post_id, 'sighting_id': sighting_id, 'job_id': job_id})

        g.conn.commit()
        test2 = g.conn.execute(text("SELECT * FROM personal_rat_sighting")).fetchall()
        print(test2)
        
        return jsonify({'message': 'Sighting added successfully!'}), 200

@app.route('/report')
def report():
        result = g.conn.execute(text("""
           SELECT 
                i.job_id as job_id, 
                i.zip_code, 
                i.borough, 
                i.result, 
                i.date,
                p.post_id as post_id,
                co.text as comment,  
                COALESCE(SUM(CASE WHEN v.up_down = TRUE THEN 1 WHEN v.up_down = FALSE THEN -1 ELSE 0 END), 0) AS like_count                                                            
            FROM 
                inspection_post AS i
            JOIN 
                post AS p ON i.job_id = p.job_id
            LEFT JOIN 
                comment_on AS co ON p.post_id = co.post_id
            LEFT JOIN 
                Vote as v on p.post_id = v.post_id
            GROUP BY 
                i.job_id, i.zip_code, i.borough, i.result, i.date, p.post_id, co.text 
            ORDER BY 
                p.post_id
        """))
        columns = result.keys()
        # rows = result.fetchall()
        rows = result.mappings() 

        # test = g.conn.execute(text("SELECT * FROM personal_rat_sighting")).fetchall()
        # print(test)
    
    # Now, we need to format this result into a list of posts, each with its own comments
        formatted_result = []
        current_post = None
        
        for row in rows:
            job_id = row['job_id']  # Accessing by column name works now
            if current_post is None or current_post['job_id'] != job_id:
                if current_post:
                    formatted_result.append(current_post)
                current_post = {
                    'job_id': job_id,
                    'zip_code': row['zip_code'],
                    'borough': row['borough'],
                    'result': row['result'],
                    'like_count': row['like_count'],
                    'post_id': row['post_id'], 
                    'date': row['date'], 
                
                    'comments': []
                }
            if row['comment']:  # If there is a comment for this row
                current_post['comments'].append({'comment_text': row['comment']})

        if current_post:
            formatted_result.append(current_post)
    
        return render_template("inspection_post.html", data=formatted_result)
        
        # columns = result.keys()  
        # formatted_result = [dict(zip(columns, row)) for row in result.fetchall()]
    
        # return render_template("inspection_post.html", data=formatted_result)

@app.route('/search_inspection', methods=['POST'])
def search_inspection():
        search = request.form['search']
    
        try:
            search_int = int(search)
            query = text("""
            SELECT 
                i.job_id as job_id, 
                i.zip_code, 
                i.borough, 
                i.result, 
                i.date,
                p.post_id as post_id, 
                co.text as comment, 
                COALESCE(SUM(CASE WHEN v.up_down = TRUE THEN 1 WHEN v.up_down = FALSE THEN -1 ELSE 0 END), 0) AS like_count                                                            
  
            FROM 
                inspection_post AS i
            JOIN 
                post AS p ON i.job_id = p.job_id
            LEFT JOIN 
                comment_on AS co ON p.post_id = co.post_id
            LEFT JOIN 
                VOte as v ON p.post_id = v.post_id
            WHERE zip_code = :search_query
            GROUP BY 
                i.job_id, i.zip_code, i.borough, i.result, i.date, p.post_id, co.text 
            ORDER BY 
                p.post_id

            """)
            result = g.conn.execute(query, {"search_query": search_int})
        
        except ValueError:
            boroughs = ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island']
    
            dates_query = text("SELECT DISTINCT date FROM inspection_post")
            dates = [row[0] for row in g.conn.execute(dates_query).fetchall()]
            
            
            if search in boroughs:
                query = text("""
                SELECT 
                    i.job_id as job_id, 
                    i.zip_code, 
                    i.borough, 
                    i.result, 
                    i.date,
                    p.post_id as post_id, 
                    co.text as comment, 
                    COALESCE(SUM(CASE WHEN v.up_down = TRUE THEN 1 WHEN v.up_down = FALSE THEN -1 ELSE 0 END), 0) AS like_count                                                            
  
                FROM 
                    inspection_post AS i
                JOIN 
                    post AS p ON i.job_id = p.job_id
                LEFT JOIN 
                    comment_on AS co ON p.post_id = co.post_id
                LEFT JOIN 
                    Vote AS v ON p.post_id = v.post_id
                WHERE borough = :search_query
                GROUP BY 
                    i.job_id, i.zip_code, i.borough, i.result, i.date, p.post_id, co.text 
                ORDER BY 
                    p.post_id

                """)
                result = g.conn.execute(query, {"search_query": search})
            else :
                try: 
                    if (datetime.strptime(search, '%Y-%m-%d').date() in dates):  
                        query = text("""
                            SELECT 
                                i.job_id as job_id, 
                                i.zip_code, 
                                i.borough, 
                                i.result, 
                                i.date,
                                p.post_id as post_id, 
                                co.text as comment,
                                COALESCE(SUM(CASE WHEN v.up_down = TRUE THEN 1 WHEN v.up_down = FALSE THEN -1 ELSE 0 END), 0) AS like_count                                                            
   
                            FROM 
                                inspection_post AS i
                            JOIN 
                                post AS p ON i.job_id = p.job_id
                            LEFT JOIN 
                                comment_on AS co ON p.post_id = co.post_id
                            LEFT JOIN 
                                Vote AS v ON p.post_id = v.post_id
                            WHERE date = :search_query
                            GROUP BY 
                                i.job_id, i.zip_code, i.borough, i.result, i.date, p.post_id, co.text 
                            ORDER BY 
                                p.post_id

                        """)
                        result = g.conn.execute(query, {"search_query": search})    
                except:
                    return render_template("inspection_post.html", data=[])
        
                columns = result.keys()
        # rows = result.fetchall()
        rows = result.mappings() 

        # test = g.conn.execute(text("SELECT * FROM personal_rat_sighting")).fetchall()
        # print(test)
    
    # Now, we need to format this result into a list of posts, each with its own comments
        formatted_result = []
        current_post = None
        
        for row in rows:
            job_id = row['job_id']  # Accessing by column name works now
            if current_post is None or current_post['job_id'] != job_id:
                if current_post:
                    formatted_result.append(current_post)
                current_post = {
                    'job_id': job_id,
                    'zip_code': row['zip_code'],
                    'borough': row['borough'],
                    'result': row['result'],
                    'like_count': row['like_count'],
                    'post_id': row['post_id'], 
                    'date': row['date'], 
                
                    'comments': []
                }
            if row['comment']:  # If there is a comment for this row
                current_post['comments'].append({'comment_text': row['comment']})

        if current_post:
            formatted_result.append(current_post)
    
        return render_template("inspection_post.html", data=formatted_result)
  




def tuple_to_dict(row, keys):
    """Convert a tuple row into a dictionary using the provided keys."""
    return dict(zip(keys, row))


@app.route('/qa', methods=['GET', 'POST'])
def qa():
    try:
        # Handle POST Requests
        if request.method == 'POST':
            # For Replies Submitted via AJAX
            if request.is_json:
                data = request.get_json()
                if 'answer' in data and 'question_id' in data:
                    answer = data['answer']
                    question_id = int(data['question_id'])
                    result2 = g.conn.execute(text("SELECT MAX(reply_id) FROM Reply"))
                    max_reply_id = result2.fetchone()[0]
                    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    if max_reply_id is None:
                        reply_id = 1
                    else:
                        reply_id = max_reply_id + 1


                    # Insert the reply into the database
                    g.conn.execute(text("""
                        INSERT INTO Reply (reply_id, question_id, answer, time)
                        VALUES (:reply_id, :question_id, :answer, :time )
                    """), {'reply_id': reply_id, 'question_id': question_id, 'answer': answer, 'time': time})

                    g.conn.commit()

                    # Return a success response
                    return jsonify({
                        'message': 'success',
                        'question_id': question_id,
                        'answer': answer,
                        'time': time, 
                    })

            # For New Questions Submitted via Form
            if 'question_text' in request.form and 'email_address' in request.form:
                question_text = request.form['question_text']
                email_address = request.form['email_address']

                # Check if the email exists in the Email table
                email_check = g.conn.execute(text("""
                    SELECT 1 FROM Email WHERE email_address = :email_address
                """), {'email_address': email_address}).fetchone()

                # Insert the email if it doesn't exist
                if not email_check:
                    g.conn.execute(text("""
                        INSERT INTO Email (email_address) VALUES (:email_address)
                    """), {'email_address': email_address})

                # Insert the question into the database
                question_result = g.conn.execute(text("""
                    INSERT INTO QandA_has (question, email_address)
                    VALUES (:question, :email_address)
                    RETURNING has_id
                """), {'question': question_text, 'email_address': email_address})

                g.conn.commit()

                new_question_id = question_result.scalar()

                # Return a success response
                return jsonify({
                    'message': 'success',
                    'question_id': new_question_id,
                    'question_text': question_text,
                    'email_address': email_address
                })

        # Handle GET Requests (Fetch Questions and Replies)
        questions_query = text("""
            SELECT has_id AS question_id, question AS question_text, email_address AS question_email
            FROM QandA_has
            ORDER BY has_id
        """)
        replies_query = text("""
            SELECT question_id, answer, time
            FROM Reply
            ORDER BY question_id, time
        """)

        questions_result = g.conn.execute(questions_query)
        replies_result = g.conn.execute(replies_query)

        # Organize questions and replies
        questions = {}
        for row in questions_result.mappings():
            questions[row['question_id']] = {
                'id': row['question_id'],
                'question_text': row['question_text'],
                'email_address': row['question_email'],
                'replies': []
            }

        for row in replies_result.mappings():
            if row['question_id'] in questions:
                questions[row['question_id']]['replies'].append({
                    'answer': row['answer'],
                    'time': row['time']
                })

        # Render the template with questions and replies
        return render_template('qa.html', questions=questions)

    except Exception as e:
        print("Error in Q&A:", str(e))
        return jsonify({'message': 'error', 'error': str(e)}), 500








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
