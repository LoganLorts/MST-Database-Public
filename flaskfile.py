import sqlite3
from flask import Flask, session, render_template, request, g, redirect, url_for
from helpers import *
import bcrypt
import hashlib
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
#app.secret_key = 
@app.before_request
def before_request():
    db = getattr(g, '_database', None)
    if app.jinja_env.globals.get('departments') is None:
        global departments
        if db is None:
            db = g._database = sqlite3.connect("MSTDatabase.db")
        cursor = db.cursor()
        cursor.execute("SELECT DISTINCT classDep FROM CLASS Order by classDep")   
        departments = cursor.fetchall()
        cursor.close()
        departments = [x[0] for x in departments]
        app.jinja_env.globals.update({
        'departments': departments
        })   
    if 'username' in session:
        global username
        username = session['username']
        app.jinja_env.globals.update({
        'Current_user': username
        })
    else:
        app.jinja_env.globals.update({
        'Current_user': 'Login'
        })

    if app.jinja_env.globals.get('department') is None:
        app.jinja_env.globals.update({
        'department': 'Department'
        })
    if app.jinja_env.globals.get('classes') is None:
        classes = []
        app.jinja_env.globals.update({
        'classes': classes
        })
    select_class = "Classes"
    app.jinja_env.globals.update({
    'select_class': select_class
    })
    
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html', success = "Registered successfully")   

@app.route('/register', methods=['POST'])
def check_register():
    email = request.form['email']
    unhashed = email
    password = request.form['password']
    password_confirmation = request.form['confirm_password']
    if password != password_confirmation:
        return render_template('register.html', error = "Passwords do not match")
    if email == "" or password == "":
        return render_template('register.html', error = "Please fill out all fields")
    if ("@mst.edu" and "@umsystem.edu") not in email:
        return render_template('register.html', error = "Please use a valid @mst or @umsystem email")
    
    salt = bcrypt.gensalt()
    email = hashlib.sha256(email.encode('utf-8')).hexdigest()
    password = bcrypt.hashpw(password.encode('utf-8'), salt)
    print(get_user(email))
    if get_user(email):
        return render_template('register.html', error = "Email already in use")
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("MSTDatabase.db")
    cursor = db.cursor()
    cursor.execute("INSERT INTO USERS (Email, Password, Salt) VALUES (?, ?, ?)", (email, password, salt))
    session['username'] = unhashed
    session['email'] = email
    db.commit()
    cursor.close()
    return render_template('register.html', error = "Registered successfully")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = check_login(email, password)
        if error == "Logged in":
            return redirect(url_for('home'))
        if error == "Admin":
            session['admin'] = 1
            return redirect(url_for('admin'), code=307)
    return render_template('login.html', error = error)
    
@app.route('/admin', methods=['POST'])
def admin():
    if session.get('admin') == None:
        return redirect(url_for('home'))
    return render_template('admin.html', reviews = [])

@app.route('/Db_add', methods=['POST'])
def Db_add():
    if session.get('admin') == None:
        return redirect(url_for('home'))
    if request.form["submit"] == "submit_class":
        classCode = request.form['classCode']
        classTitle = request.form['classTitle']
        classDep = request.form['classDep']
        Description = request.form['Description']
        Description = Description.replace("'", "")
        Description = Description.replace('"', "")
        Description = Description.lstrip()
        if classCode == "" or classTitle == "" or classDep == "":
            return render_template('admin.html', error = "Please fill out all fields")
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect("MSTDatabase.db")
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM CLASS WHERE classCode = ? AND classDep = ?", (classCode, classDep))
        if cursor.fetchone()[0] == 1:
            cursor.close()
            return render_template('admin.html', error = "Class already exists")
        cursor.execute("INSERT INTO CLASS (ClassCode, ClassTitle, ClassDep, Description) VALUES (?, ?, ?, ?)", (classCode, classTitle, classDep, Description))
        db.commit()
        cursor.close()
    elif(request.form["submit"] == "submit_teacher"):
        teacher = request.form['teacherName']
        teacherEmail = request.form['teacherEmail']
        if teacher == "":
            return render_template('admin.html', error = "Please fill out Teacher Name")
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect("MSTDatabase.db")
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM TEACHER WHERE name = ?", (teacher,))
        if cursor.fetchone()[0] == 1:
            cursor.close()
            return render_template('admin.html', error = "Teacher already exists")
        cursor.execute("INSERT INTO TEACHER (Name, Email) VALUES (?, ?)", (teacher, teacherEmail))
        db.commit()
        cursor.close()
    elif(request.form["submit"] == "Select_Comments"):
        classCode = request.form['classCode']
        classDep = request.form['classDep']
        reviews = get_review_admin(classCode, classDep)
        return render_template('admin.html', reviews = reviews)
    elif(request.form["submit"] == "Remove_Comment"):
        classCode = request.form['classCode']
        classDep = request.form['classDep']
        email = request.form['UsrEmail']
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect("MSTDatabase.db")
        cursor = db.cursor()
        cursor.execute("DELETE FROM REVIEW WHERE classCode = ? AND classDep = ? AND Email = ?", (classCode, classDep, email))
        db.commit()
        cursor.close()
        return render_template('admin.html', reviews = [])

    return redirect(url_for('admin'), code=307)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('email', None)
    session.pop('admin', None)
    return redirect(url_for('home'))


@app.route('/search', methods=['POST'])
def search():
    search = request.form['search']
    if search == "":
        return redirect(url_for('home'))
    search = search.split()
    class_num = 0
    class_title = ''
    if len(search) == 1:
        try:
            search[0] = int(search[0])
            class_num = search[0]
            class_title = ''
        except:
            class_title = search[0]
            class_title = ''.join(class_title)
    elif len(search) == 2:
        contains_num = True
        try:
            search[0] = int(search[0])
            class_num = search[0]
            class_title = search[1:]
            class_title = ''.join(class_title)
        except:
            contains_num = False
        try:
            class_num = int(search[-1])
            class_title = search[:-1]
            class_title = ''.join(class_title)
        except:
            contains_num = False
        if contains_num == False:
            class_num = 0
            class_title = ''.join(search)
        
    classes,  match = search_db(class_num, class_title)
    if match == 0:
        return render_template('index.html', search = search, error = "No results found")
    if match == 1:
        Department = classes[0][2]
        ClassCode = str(classes[0][0])
        app.jinja_env.globals.update({
        'department': Department
        })
        classes = get_all_classes(Department)
        classes = [str(x[0]) + " " + x[1] for x in classes]
        app.jinja_env.globals.update({
        'classes': classes
        })
        return redirect(url_for('class_page', DepCode=Department+ClassCode))
    if match == 2:
        Department = "Department"
        j_classes = []
        app.jinja_env.globals.update({
        'department': Department
        })
        app.jinja_env.globals.update({
        'classes': j_classes
        })
        return render_template('search.html', body_classes = classes)
        
        
#from itsdangerous import URLSafeTimedSerializer

#from project import app


#def generate_confirmation_token(email):
    #serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    #return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


#def confirm_token(token, expiration=3600):
    #serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    #try:
        #email = serializer.loads(
            #token,
            #salt=app.config['SECURITY_PASSWORD_SALT'],
            #max_age=expiration
        #)
    #except:
        #return False
    #return email

@app.route('/department', methods=['POST'])
def select_department():
    department = request.form['departments']
    app.jinja_env.globals.update({
        'department': department
        })
    return redirect(url_for('department_page', Department=department))

@app.route('/<Department>/department_page' , methods=['GET'])
def department_page(Department):
    classes = get_all_classes(Department)
    classes = [str(x[0]) + " " + x[1] for x in classes]
    app.jinja_env.globals.update({
    'classes': classes
    })
    app.jinja_env.globals.update({
    'select_class': "Classes"
    })
    return render_template('department.html',  department= Department, classes = classes)

@app.route('/<department>/select_class', methods=['POST'])
def select_class(department):
    classInfo = request.form['classes']
    classCode = classInfo.split()[0]
    classDep = department
    select_class = classInfo
    app.jinja_env.globals.update({
        'select_class': select_class
        })
    return redirect(url_for('class_page', DepCode=classDep+classCode))

@app.route('/<DepCode>/class_page' , methods=['GET'])
def class_page(DepCode):
    Department = DepCode[:-4]
    ClassCode = DepCode[-4:]
    information = get_class(ClassCode, Department)
    try:
        information = information[0]
        reviews = get_reviews(ClassCode, Department)
        avg = get_avg_rating(ClassCode, Department)
        return render_template('class.html', select_class = (str(information[1]) +" "+ information[2]), class_info = information[0], class_code = information[1], class_name=information[2], reviews=reviews, avg=avg)
    except:
        return redirect(url_for(home))

@app.route('/<DepCode>/review', methods=['GET','POST'])
def review(DepCode):
    if request.method == 'GET':
        return render_template('review.html', DepCode=DepCode)
    else:
        Department = DepCode[:-4]
        ClassCode = DepCode[-4:]
        rating = request.form["Rating"]
        teacher = request.form["Teacher"]
        teacher_rating = request.form["TeacherRating"]
        workload_rating = request.form["WorkloadRating"]
        comment = request.form["Comment"]
        Mandatory = request.form["MandatoryAttendance"]
        
        
        if rating == "" or teacher_rating == "" or workload_rating == "" or teacher == "" or Mandatory == "Select":
            return render_template('review.html', DepCode=DepCode, error = "Please fill out all fields (comment is not necessary)")
        if session.get('username') == None:
            return render_template('review.html', DepCode=DepCode, error = "Please login to leave a review (this is to prevent multiple reviews from one user, email is not saved in any accessible format)")
        if Mandatory == "Yes":
            Mandatory = 1
        else:
            Mandatory = 0
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect("MSTDatabase.db")
        cursor = db.cursor()
        current_user = session['email']
        cursor.execute("SELECT COUNT(*) FROM REVIEW WHERE classCode = ? AND classDep = ? AND Email = ?", (ClassCode, Department, current_user))
        if cursor.fetchone()[0] == 1:
            cursor.close()
            return render_template('review.html', DepCode=DepCode, error = "You have already left a review for this class")
        else:
            print(current_user)
            cursor.execute("INSERT INTO Review (ClassCode, ClassDep, Rating, TeacherRating, WorkloadRating, Comment, Teacher, Email, MandatoryAttendence) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (ClassCode, Department, rating, teacher_rating, workload_rating, comment, teacher, current_user, Mandatory))
            db.commit()
            cursor.close()
            return redirect(url_for('class_page', DepCode=DepCode))

@app.errorhandler(HTTPException)
def http_error_handler(error):
    return redirect(url_for('home'))
    
    
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
if __name__ == '__main__':
    app.run(debug=True)