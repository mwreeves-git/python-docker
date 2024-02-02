### Conda ###
# conda activate docker_3.9
# cd C:\Users\mwree\OneDrive\Documents\git\birdle-api
# python -m venv .venv

### CMD ###
# .venv\Scripts\activate
# python -m pip install -r requirements.txt
# python -m flask run

### Browser ###
# http://localhost:5000/add?bird=Cardinal&location=Patio&user=Other&pass=birdlebirdlebirdle
# http://localhost:5000/undo?pass=birdlebirdlebirdle

### CMD ###
# cd C:\Users\mwree\OneDrive\Documents\git\birdle-api
# docker init #### Build the docker file
# python -m flask run --host=0.0.0.0 #### Run the Flask alone
# docker compose up --build #### Run the whole docker

# docker build -t birdle-api . #### Build the image
# docker run -dp 127.0.0.1:5000:5000 birdle-api #### Run the image
# docker compose down

# docker tag birdle-api mwreeves/birdle-api
# docker push mwreeves/birdle-api


from flask import Flask, request
import pymssql
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

conn_host ='192.168.68.118'
conn_user = 'SA'
conn_pass = 'nimdA!!!'
conn_db = 'Shiny'


app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["2 per minute", "1 per second"],
    storage_uri="memory://",
    strategy="fixed-window", # or "moving-window"
)

@app.route('/add')
@limiter.limit("1 per 5 seconds")
def birdle_add():
    url_bird = request.args.get('bird') # url_bird = 'Cardinal'
    url_user = request.args.get('user') # url_user = 'Other'
    url_location = request.args.get('location') # url_location = 'Patio'
    url_pass = request.args.get('pass')
    if url_pass == 'birdlebirdlebirdle':
        conn = pymssql.connect(conn_host, conn_user, conn_pass, conn_db)
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT bird_id FROM [Shiny].[dbo].[birdle_birds] where bird_name = '{}'".format(url_bird))
        cursor_data = cursor.fetchall()
        if len(cursor_data) > 0:
            bird_id = cursor_data[0]['bird_id']
            cursor.execute("insert into [dbo].[birdle_sightings] values({}, '{}', '{}', getdate())".format(bird_id, url_location, url_user))
            conn.commit()
            cursor.execute("""select count(1) as bird_count FROM [Shiny].[dbo].[birdle_sightings] where convert(varchar(10), sighting_dt, 126) = convert(varchar(10), getdate(), 126)""")
            cursor_data = cursor.fetchall()
            bird_count = cursor_data[0]['bird_count']
            output = 'Birdles Today: ' + str(bird_count)
        else:
            output = 'Bird Not Found'
        conn.close()
    else:
        output = 'Access Denied: Wrong Pass'
    return output

@app.route('/undo')
@limiter.limit("1 per 20 seconds")
def birdle_undo():
    url_pass = request.args.get('pass')
    if url_pass == 'birdlebirdlebirdle':
        conn = pymssql.connect(conn_host, conn_user, conn_pass, conn_db)
        cursor = conn.cursor(as_dict=True)
        cursor.execute("exec dbo.birdle_undo_sighting")
        conn.commit()
        conn.close()
        cursor.execute("""select count(1) as bird_count FROM [Shiny].[dbo].[birdle_sightings] where convert(varchar(10), sighting_dt, 126) = convert(varchar(10), getdate(), 126)""")
        cursor_data = cursor.fetchall()
        bird_count = cursor_data[0]['bird_count']
        output = 'Birdles Today: ' + str(bird_count)
    else:
        output = 'Access Denied: Wrong Pass'
    return output

@app.route('/test')
@limiter.exempt
def birdle_test():
    conn = pymssql.connect(conn_host, conn_user, conn_pass, conn_db)
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT count(1) as count FROM [Shiny].[dbo].[birdle_other]')
    cursor_data = cursor.fetchall()
    row_count = cursor_data[0]['count']
    conn.close()
    return str(row_count)