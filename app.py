import plotly.graph_objs as go

from cs50 import SQL
from helpers import login_required, get_framework, get_head, export_data
from werkzeug.security import check_password_hash, generate_password_hash
from flask import session, flash, render_template, Flask, request, redirect, jsonify
from flask_session import Session
from plotly.subplots import make_subplots
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///WORK.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/', methods=["GET", "POST"])
@login_required
def index():

    if request.method == "POST":

        start = '2010-10-10' if not request.form.get("from") else request.form.get("from").replace('T', ' ')
        end = 'CURRENT_DATE' if not request.form.get("to") else request.form.get("to").replace('T', ' ')
        weldpart = None if not request.form.get("weldpart") else request.form.get("weldpart")
        wp = None if not request.form.get("wp") else request.form.get("wp")
        cell = request.form.get("cell")
        robot = request.form.get("robot")
        alarm_placeholder = None
        values = [weldpart, weldpart, wp, wp, cell, cell, robot, robot, start, end]
        
        if request.form.get("alarm") == 'All alarms':
            alarm_placeholder = 'IS NOT NULL'
        elif request.form.get("alarm") == 'None':
            alarm_placeholder = 'IS NULL'
        else:
            alarm = request.form.get("alarm")
            alarm_placeholder = '= ? OR ? IS NULL'
            values = [weldpart, weldpart, wp, wp, cell, cell, robot, robot, alarm, alarm, start, end]

        try:
            weldpoints = db.execute(f"""
                SELECT *
                FROM data
                WHERE 
                    (Part = ? OR ? IS NULL) AND
                    (Wp = ? OR ? IS NULL) AND
                    (Cell = ? OR ? IS NULL) AND
                    (Robot = ? OR ? IS NULL) AND
                    (Alarm {alarm_placeholder} ) AND
                    Date BETWEEN ? AND ?                
                ORDER BY Date DESC
                LIMIT 30;""", *values
            )
        except Exception as e:
            print(f'Error: {e}')

        critics = critical_weldpoints()
        cell = cells()
        alarm = alarms()
        session['limit'] = None

        return render_template("main.html", weldpoints=weldpoints, critics=critics, cells=cell, alarms=alarm)
        
    else:
        critics = critical_weldpoints()
        cell = cells()
        alarm = alarms()
        session['limit'] = None

        return render_template("main.html", critics=critics, cells=cell, alarms=alarm)


@app.route('/limits')
@login_required
def limits():
    limit_name = request.args.get('limit_name')
    
    limit = db.execute('SELECT * FROM limits WHERE name = ?', limit_name)

    session['limit'] = limit

    return jsonify({"status": "success", "message": "Successfully applied"})


@app.route('/graph', methods=["GET", "POST"])
@login_required
def graph():

    if request.method == "POST":

        if request.form.get("parameter"):        
            parameter = request.form.get("parameter")
            selected_parameters = request.form.getlist("selected_parameters")

            maxLenTime = 0
            maxTime = []
            fig = make_subplots(rows=1,cols=1)

            for p in selected_parameters:
                
                query = f'''
                        SELECT "{parameter}", "Time [s]" FROM Parameters
                        JOIN Relation ON Parameters.id = Relation.id_parameter
                        JOIN data ON Relation.id_data = data.id
                        WHERE data.id = ?'''
                    
                selected_weldpoint = db.execute(query, p) 

                name = db.execute('''
                    SELECT Part, Wp FROM data
                    WHERE id = ?''',
                    p)

                time = []
                parameterY = []
                for d in selected_weldpoint:
                    time.append(d["Time [s]"])
                    parameterY.append(d[parameter])

                if len(time) > maxLenTime:
                    maxLenTime = len(time)
                    maxTime = time

                fig.add_trace(go.Scatter(x=time, 
                                        y=parameterY, 
                                        mode='lines', 
                                        name= name[0]['Part'] + '-' + str(name[0]['Wp'])))

                fig.update_layout(title='Behavior Weldpoints', xaxis_title='Time [s]', 
                                yaxis_title=parameter)

            if session['limit'] and session['limit'][0]['parameter'] == parameter:
                limit = session['limit'][0]

                fig.add_trace(go.Scatter(x=maxTime,
                            y=[limit['bottom']] * maxLenTime, 
                            mode='lines', 
                            line=dict(color='#FFA500', dash='dash'),
                            name= 'Lower limit'))
                fig.add_trace(go.Scatter(x=maxTime,
                            y=[limit['top']] * maxLenTime, 
                            mode='lines', 
                            line=dict(color='#FFA500', dash='dash'),
                            name= 'Upper limit'))

            plot_div = fig.to_html(full_html=False)

            return jsonify({'status': 'success', 'plot_div': plot_div}) 
        
        else:

            return jsonify({'status': 'error', 'message': 'Must select a parameter'})
        
    else:
        return redirect("/")


@app.route('/create', methods=["GET", "POST"])
@login_required
def create():

    if request.method == "POST":

        if request.form.get("parameter_limits") and \
            request.form.get("bottom") and \
            request.form.get("top") and \
            request.form.get("name"):
            
            try:
                bottom = float(request.form.get("bottom"))
                top = float(request.form.get("top"))
            except ValueError:
                return jsonify({"status": "error", "message": "Limits must be numbers"})
            
            try:
                parameter_limits = request.form.get("parameter_limits")
                graph_name = request.form.get("name")
                
                db.execute("""INSERT INTO limits (bottom, top, name, parameter) 
                        VALUES (?, ?, ?, ?)""",
                        bottom, top, graph_name, parameter_limits)
                
                return jsonify({"status": "success", "message": "Successfully created"})
            
            except Exception as e:
                return jsonify({"status": "error", "message": "Error creating limit"})

        else:    
            return jsonify({"status": "error", "message": "Incomplete form data"})
        
    else:
        return redirect("/")


@app.route('/get_limits', methods=["GET", "POST"])
@login_required
def get_limits():

    if request.method == "POST":

        parameter = request.form.get('parameter')

        limits = db.execute("SELECT name FROM limits WHERE parameter = ?", parameter)

        limit_names = [limit['name'] for limit in limits]

        return jsonify({"limits": limit_names})
    
    else:
        return redirect("/")


@app.route('/login', methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            flash ("Must provide a username")
            return render_template("login.html")
        
        elif not request.form.get("password"):
            flash ("Must provide password")
            return render_template("login.html")
        
        username = request.form.get("username")
        password = request.form.get("password")

        username_valid = db.execute("SELECT * FROM users WHERE user = ?", (username,))
        
        if len(username_valid) != 1 or not check_password_hash(
            username_valid[0]["password"], password):
            flash ("Invalid user")
            return render_template("login.html")
        
        session["user_id"] = username_valid[0]["id"]
        session["username"] = username_valid[0]["user"]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
@login_required
def register():
    
    if request.method == 'POST':
        if not request.form.get("username"):
            flash ("Must provide a username")
            return render_template("register.html")

        elif not request.form.get("password"):
            flash ("Must provide password")
            return render_template("register.html")
        
        elif not request.form.get("confirm"):
            flash('must confirm password')
            return render_template("register.html")

        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if password != confirm:
            flash('incorrect password confirmation')
            return render_template("register.html")

        username_valid = db.execute("SELECT * FROM users WHERE user = ?", (username,))
        
        if username_valid:
            flash ("user already in use")
            return render_template("register.html")
        
        db.execute('''
            INSERT INTO users (user, password)
            VALUES (?, ?)''',
            username, generate_password_hash(password))
        
        username_ok = db.execute('''SELECT * FROM users 
            WHERE user = ?''',
            username)
        
        session["user_id"] = username_ok[0]["id"]
        session["username"] = username_ok[0]["user"]

        return redirect("/")

    else:
        return render_template("register.html")


@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')


def cells():
    cells = db.execute('''
        SELECT Cell FROM data
        GROUP BY Cell''')
    
    return cells
    
def alarms():
    alarms = db.execute('''
        SELECT Alarm FROM data
        GROUP BY Alarm''')
    
    return alarms

def critical_weldpoints():
    critical = db.execute('''
        SELECT id, COUNT(*) as total
        FROM data
        WHERE Alarm IS NOT NULL
        GROUP BY Part, Wp
        ORDER BY total DESC
        LIMIT 4;
        ''')
    
    placeholders = ', '.join('?' * len(critical))
    ids = [item["id"] for item in critical]

    critical_welds = db.execute(f'''
        SELECT Part, Wp, Cell, Robot, id FROM data
        WHERE id IN ({placeholders});
        ''', *ids)
    
    for c in critical_welds:
        c["total"] = next(item["total"] for item in critical if item["id"] == c['id'])

    return critical_welds


def run_flask_app():
    app.run()


def main():     
    event_handler = FileSystemEventHandler()
    event_handler.on_created = on_created

    path = "sample"
    observer = Observer()   
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    try:
        run_flask_app()
    except KeyboardInterrupt:
        observer.stop()
        observer.join()


def on_created(event):
    path = event.src_path
    if path.endswith('.xls'):
        sheet = "AllData"
        columns = ["Time [s]", "Motor 1 current [A]", "Welding Current [A]", "Welding Voltage [V]", "Wire feed 1 speed [m/min]"]
        
        try:
            df = get_framework(path, sheet, columns)
            head = get_head(path, sheet)

            export_data(head, df)

        except Exception as e:
            print(f"Error al procesar el archivo {path}: {str(e)} ")


if __name__ == "__main__":
    main()
