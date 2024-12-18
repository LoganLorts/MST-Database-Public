import sqlite3
from flask import session, request, g, redirect, url_for
import bcrypt
import hashlib

def check_login(email, password):
    unhashed = email
    password = str(password)
    email = hashlib.sha256(email.encode('utf-8')).hexdigest()
    user = get_user(email)
    if not user:
        return "Invalid email"
    salt = user[0][2]
    password = bcrypt.hashpw(password.encode('utf-8'), salt)
    if password == user[0][1]:
        session['username'] = unhashed
        session['email'] = email
        if check_if_admin(email) == 1:
            return "Admin"
        return "Logged in"
    else:
        return "Invalid password"
    
    
def check_if_admin(email):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("MSTDatabase.db")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM ADMIN WHERE email = ?", (email,))
    admin_data = cursor.fetchall()
    cursor.close()
    if len(admin_data) == 0:
        return 0
    return 1


def get_all_classes(Department):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("MSTDatabase.db")
    cursor = db.cursor()
    cursor.execute("SELECT ClassCode, ClassTitle FROM CLASS WHERE ClassDep = ? Order by ClassCode", (Department,))
    all_data = cursor.fetchall()
    cursor.close()
    return all_data


def get_reviews(classCode, classDep):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("MSTDatabase.db")
    cursor = db.cursor()
    cursor.execute("SELECT Rating, TeacherRating, WorkloadRating, Comment, Teacher, MandatoryAttendence FROM REVIEW WHERE classCode = ? AND classDep = ? Order by Teacher", (classCode, classDep))   
    all_data = cursor.fetchall()
    cursor.close()
    return all_data


def get_review_admin(classCode, classDep):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("MSTDatabase.db")
    cursor = db.cursor()
    cursor.execute("SELECT Comment, Teacher, Email, ClassDep, ClassCode FROM REVIEW WHERE classCode = ? AND classDep = ?", (classCode, classDep))   
    all_data = cursor.fetchall()
    cursor.close()
    return all_data


def get_avg_rating(classCode, classDep):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("MSTDatabase.db")
    cursor = db.cursor()
    cursor.execute("SELECT Teacher, ROUND(AVG(Rating), 2), ROUND(AVG(TeacherRating), 2), ROUND(AVG(WorkloadRating), 2) FROM REVIEW WHERE classCode = ? AND classDep = ? Group by(Teacher)", (classCode, classDep))   
    all_data = cursor.fetchall()
    cursor.close()
    return all_data


def get_class(classCode, classDep):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("MSTDatabase.db")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM CLASS WHERE classCode = ? AND classDep = ?", (classCode, classDep))   
    all_data = cursor.fetchall()
    cursor.close()
    return all_data


def get_users():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("MSTDatabase.db")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM USERS")   
    all_data = cursor.fetchall()
    cursor.close()
    return all_data


def get_user(email):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("MSTDatabase.db")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM USERS WHERE email = ?", (email,))   
    user = cursor.fetchall()
    cursor.close()
    return user


def search_db(class_num, class_title):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("MSTDatabase.db")
    cursor = db.cursor()
    if class_num == 0:
        cursor.execute("SELECT ClassCode, ClassTitle, ClassDep FROM CLASS WHERE ClassTitle LIKE ?", ('%'+class_title+'%',))
    elif(class_title == ""):
        cursor.execute("SELECT ClassCode, ClassTitle, ClassDep FROM CLASS WHERE ClassCode = ?", (class_num,))
    else:
        cursor.execute("SELECT ClassCode, ClassTitle, ClassDep FROM CLASS WHERE ClassCode = ? AND ClassTitle LIKE ?", (class_num, '%'+class_title+'%'))
    all_data = cursor.fetchall()
    print(all_data)
    cursor.close()
    if len(all_data) == 0:
        return all_data, 0
    if len(all_data) == 1:
        return all_data, 1
    return all_data, 2
    