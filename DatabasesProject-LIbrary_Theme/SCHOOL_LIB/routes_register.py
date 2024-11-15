from flask import Flask, render_template, request, make_response, flash, redirect, url_for, abort, jsonify
from flask_mysqldb import MySQL
from SCHOOL_LIB import app, db ## initially created by __init__.py, need to be used here
import json

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/process_registration', methods=['POST'])
def process_registration():
    username = request.form['username']
    password = request.form['password']
    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']
    postal_code = request.form['postal_code']
    phone = request.form['phone']
    age = request.form['age']
    sex = request.form['sex']
    class_ = request.form['class']
    user_type = request.form['user_type']
    school_id = request.form['school_id']

    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Name: {name}")
    print(f"Surname: {surname}")
    print(f"Email: {email}")
    print(f"Postal Code: {postal_code}")
    print(f"Phone: {phone}")
    print(f"Age: {age}")
    print(f"Sex: {sex}")
    print(f"Class: {class_}")
    print(f"User Type: {user_type}")
    print(f"School ID: {school_id}")

    query = """INSERT INTO library_user (username, user_password, user_name, user_surname, user_email, operator_postal_code, phone, user_age, user_sex, user_class, user_type, able_status, school_id)
                VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {})""".format(
                    username, password, name, surname, email, postal_code, phone, age, sex, class_, user_type, 'new', school_id)
    print(query)
    cur = db.connection.cursor()
    cur.execute(query)
    db.connection.commit()
    cur.close()

    
    return username

@app.route('/new_users', methods=['GET', 'POST'])
def new_users():
    if request.method == 'POST':
        user_id = request.form['user_id']
        print(user_id)
        query = "UPDATE library_user SET able_status = 'OK' WHERE user_id = {};".format(user_id)
        print(query)
        cur = db.connection.cursor()
        cur.execute(query)
        db.connection.commit()
        cur.close()

    uid = request.cookies.get('id')
    if uid == None:
        return render_template('noaccess.html')
    uid = int(uid)
    if not is_operator(uid):
        return render_template('noaccess.html')

    query = "SELECT lu2.*, s.school_name FROM library_user lu1 JOIN library_user lu2 ON lu1.school_id = lu2.school_id JOIN school s ON s.school_id = lu1.school_id WHERE lu1.user_id = {} AND lu2.user_id <> {} AND lu2.able_status = 'new'".format(uid, uid)
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()

    res = list(rv)
    print(res)

    return render_template('new_users.html', library_users = res)

def is_operator(uid):
    # returns 1 if uid user is operator, 0 if not
    query = 'SELECT is_operator FROM library_user WHERE user_id = {};'.format(uid)
    print('check1')
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()
    print(rv[0][0])
    return int(rv[0][0])

@app.route('/new_reviews', methods=['GET', 'POST'])
def new_reviews():
    operator_id = request.cookies['id']
    if request.method == 'POST':
        user_id = request.form['user_id']
        book_id = request.form['book_id']
        print(user_id)
        print(book_id)
        query = "UPDATE reviews SET approve_status = 'Approved' WHERE user_id = {} AND book_id = {};".format(user_id, book_id)
        query2 = "UPDATE library_user SET  reviews_approved = reviews_approved + 1 WHERE user_id = {};".format(operator_id)
        
        print(query)
        cur = db.connection.cursor()
        cur.execute(query)
        db.connection.commit()
        cur.close()

        cur2 = db.connection.cursor()
        cur2.execute(query2)
        db.connection.commit()
        cur.close()

        print(query2)

    uid = request.cookies.get('id')
    if uid == None:
        return render_template('noaccess.html')
    uid = int(uid)
    if not is_operator(uid):
        return render_template('noaccess.html')
    
    querySID = "SELECT school_id FROM library_user WHERE user_id = {};".format(operator_id) #which school am i in?
    cur2 = db.connection.cursor()
    cur2.execute(querySID)
    rv2 = cur2.fetchall()
    rv2=list(rv2)
    rv2 = rv2[0][0]
    print(rv2)

    
    

    query = "SELECT * FROM school_reviews WHERE approve_status = 'Pending' AND school_id = {};".format(rv2)
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()

    res = list(rv)
    

    return render_template('new_reviews.html', bookReview = res)



@app.route('/new_borrows', methods=['GET', 'POST'])
def new_borrows():
    operator_id = request.cookies['id']
    if request.method == 'POST':
        user_id = request.form['user_id']
        book_id = request.form['book_id']
        print(user_id)
        print(book_id)
        query = "UPDATE borrows SET approve_status = 'Approved' WHERE user_id = {} AND book_id = {};".format(user_id, book_id)
        query2 = "UPDATE library_user SET  borrows_approved = borrows_approved + 1 WHERE user_id = {};".format(operator_id)
        query3 = "UPDATE contains SET number_of_copies = number_of_copies - 1 WHERE book_id = {} AND school_id = {};".format(book_id, request.form['school_id'])
        
        print(query)
        cur = db.connection.cursor()
        cur.execute(query)
        db.connection.commit()
        cur.close()

        cur2 = db.connection.cursor()
        cur2.execute(query2)
        db.connection.commit()
        cur.close()

        print(query2)

        cur3 = db.connection.cursor()
        cur3.execute(query3)
        db.connection.commit()
        cur3.close()
        print(query3)

    uid = request.cookies.get('id')
    if uid == None:
        return render_template('noaccess.html')
    uid = int(uid)
    if not is_operator(uid):
        return render_template('noaccess.html')
    
    #Sort out overdue borrows
    queryOverdue = """UPDATE borrows
                    SET approve_status = 'Overdue'
                    WHERE approve_status = 'Approved' AND date_of_borrow < DATE_SUB(CURDATE(), INTERVAL 7 DAY);"""
    
    ovr = db.connection.cursor()
    ovr.execute(queryOverdue)
    db.connection.commit()
    ovr.close()
    
    querySID = "SELECT school_id FROM library_user WHERE user_id = {};".format(operator_id) #which school am i in?
    cur2 = db.connection.cursor()
    cur2.execute(querySID)
    rv2 = cur2.fetchall()
    rv2=list(rv2)
    rv2 = rv2[0][0]
    print(rv2)

    


    query = "SELECT * FROM school_borrows WHERE approve_status = 'Pending' AND school_id = {};".format(rv2) #pending request from the RIGHT school
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()

    res = list(rv)
    print(res)


    return render_template('new_borrows.html', bookBorrow = res, school_id = rv2)

@app.route('/archived_borrows', methods=['GET', 'POST'])
def archived_borrows():
    operator_id = request.cookies['id']
    if request.method == 'POST': #This means 'Delete' was pressed
        user_id = request.form['user_id']
        book_id = request.form['book_id']
        print(user_id)
        print(book_id)
        query = "DELETE FROM borrows WHERE user_id = {} AND book_id = {};".format(user_id, book_id)
        print(query)
        cur = db.connection.cursor()
        cur.execute(query)
        db.connection.commit()
        cur.close()

    uid = request.cookies.get('id')
    if uid == None:
        return render_template('noaccess.html')
    uid = int(uid)
    if not is_operator(uid):
        return render_template('noaccess.html')
    
    #Sort out overdue borrows
    queryOverdue = """UPDATE borrows
                    SET approve_status = 'Overdue'
                    WHERE approve_status = 'Approved' AND date_of_borrow < DATE_SUB(CURDATE(), INTERVAL 7 DAY);"""
    
    ovr = db.connection.cursor()
    ovr.execute(queryOverdue)
    db.connection.commit()
    ovr.close()
    
    querySID = "SELECT school_id FROM library_user WHERE user_id = {};".format(operator_id) #which school am i in?
    cur2 = db.connection.cursor()
    cur2.execute(querySID)
    rv2 = cur2.fetchall()
    rv2=list(rv2)
    rv2 = rv2[0][0]
    print(rv2)

    query = "SELECT * FROM school_borrows WHERE approve_status IN ('Approved', 'Overdue') AND school_id = {};".format(rv2) #pending request from the RIGHT school
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()
    res = list(rv)
    print(res)

    return render_template('archived_borrows.html', bookBorrow = res, school_id = rv2)

@app.route('/return', methods=['GET', 'POST'])
def returnBook():
    operator_id = request.cookies['id']
    if request.method == 'POST': 
        user_id = request.form['user_id']
        book_id = request.form['book_id']
        print(user_id)
        print(book_id)
        query =  "INSERT INTO returned(user_id, book_id, date_of_return) VALUES ({}, {}, CURDATE());".format(user_id, book_id)
        query2 = """UPDATE borrows
                    SET approve_status = 'Returned'
                    WHERE user_id = {} AND book_id = {};""".format(user_id, book_id)
        
        print(query)
        cur = db.connection.cursor()
        cur.execute(query)
        db.connection.commit()
        cur.close()

        print(query2)
        cur2 = db.connection.cursor()
        cur2.execute(query2)
        db.connection.commit()
        cur2.close()

    uid = request.cookies.get('id')
    if uid == None:
        return render_template('noaccess.html')
    uid = int(uid)
    if not is_operator(uid):
        return render_template('noaccess.html')
    
    #Sort out overdue borrows
    queryOverdue = """UPDATE borrows
                    SET approve_status = 'Overdue'
                    WHERE approve_status = 'Approved' AND date_of_borrow < DATE_SUB(CURDATE(), INTERVAL 7 DAY);"""
    
    ovr = db.connection.cursor()
    ovr.execute(queryOverdue)
    db.connection.commit()
    ovr.close()
    
    querySID = "SELECT school_id FROM library_user WHERE user_id = {};".format(operator_id) #which school am i in?
    cur2 = db.connection.cursor()
    cur2.execute(querySID)
    rv2 = cur2.fetchall()
    rv2=list(rv2)
    rv2 = rv2[0][0]
    print(rv2)

    query = "SELECT * FROM school_borrows WHERE approve_status IN ('Approved', 'Overdue') AND school_id = {};".format(rv2) #pending request from the RIGHT school
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()
    res = list(rv)
    print(res)

    return render_template('archived_borrows.html', bookBorrow = res, school_id = rv2)

@app.route('/archived_reservations', methods=['GET', 'POST'])
def archived_reservations():
    operator_id = request.cookies['id']
    if request.method == 'POST': #This means 'Delete' was pressed
        user_id = request.form['user_id']
        book_id = request.form['book_id']
        print(user_id)
        print(book_id)
        query = "DELETE FROM reservations WHERE user_id = {} AND book_id = {};".format(user_id, book_id)
        print(query)
        cur = db.connection.cursor()
        cur.execute(query)
        db.connection.commit()
        cur.close()

    uid = request.cookies.get('id')
    if uid == None:
        return render_template('noaccess.html')
    uid = int(uid)
    if not is_operator(uid):
        return render_template('noaccess.html')
    
    #Sort out overdue reservations
    queryOverdue = """UPDATE reservations
                    SET approve_status = 'Overdue'
                    WHERE approve_status = 'Approved' AND deadline_of_reservation < CURDATE();"""
    
    ovr = db.connection.cursor()
    ovr.execute(queryOverdue)
    db.connection.commit()
    ovr.close()
    print(queryOverdue)
    
    querySID = "SELECT school_id FROM library_user WHERE user_id = {};".format(operator_id) #which school am i in?
    cur2 = db.connection.cursor()
    cur2.execute(querySID)
    rv2 = cur2.fetchall()
    rv2=list(rv2)
    rv2 = rv2[0][0]
    print(rv2)

    query = "SELECT * FROM school_reservations WHERE approve_status IN ('Approved', 'Overdue') AND school_id = {};".format(rv2) #pending request from the RIGHT school
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()
    res = list(rv)
    print(res)

    return render_template('archived_reservations.html', reserve = res, school_id = rv2)

@app.route('/makeBorrow', methods=['GET', 'POST'])
def makeBorrow():
    operator_id = request.cookies['id']
    if request.method == 'POST': 
        user_id = request.form['user_id']
        book_id = request.form['book_id']
        print(user_id)
        print(book_id)
        query =  "INSERT INTO borrows(user_id, book_id, date_of_borrow, approve_status) VALUES ({}, {}, CURDATE(), 'Approved');".format(user_id, book_id)
        query2 = "DELETE FROM reservations WHERE user_id = {} AND book_id = {};".format(user_id, book_id)
        
        print(query)
        cur = db.connection.cursor()
        cur.execute(query)
        db.connection.commit()
        cur.close()

        print(query2)
        cur2 = db.connection.cursor()
        cur2.execute(query2)
        db.connection.commit()
        cur2.close()

    uid = request.cookies.get('id')
    if uid == None:
        return render_template('noaccess.html')
    uid = int(uid)
    if not is_operator(uid):
        return render_template('noaccess.html')
    
    #Sort out overdue borrows
    queryOverdue = """UPDATE borrows
                    SET approve_status = 'Overdue'
                    WHERE approve_status = 'Approved' AND date_of_borrow < DATE_SUB(CURDATE(), INTERVAL 7 DAY);"""
    
    ovr = db.connection.cursor()
    ovr.execute(queryOverdue)
    db.connection.commit()
    ovr.close()
    
    querySID = "SELECT school_id FROM library_user WHERE user_id = {};".format(operator_id) #which school am i in?
    cur2 = db.connection.cursor()
    cur2.execute(querySID)
    rv2 = cur2.fetchall()
    rv2=list(rv2)
    rv2 = rv2[0][0]
    print(rv2)

    query = "SELECT * FROM school_borrows WHERE approve_status IN ('Approved', 'Overdue') AND school_id = {};".format(rv2) #pending request from the RIGHT school
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()
    res = list(rv)
    print(res)

    return render_template('archived_borrows.html', bookBorrow = res, school_id = rv2)

@app.route('/new_reservations', methods=['GET', 'POST'])
def new_reservations():
    operator_id = request.cookies['id']
    if request.method == 'POST':
        user_id = request.form['user_id']
        book_id = request.form['book_id']
        print(user_id)
        print(book_id)
        query = "UPDATE reservations SET approve_status = 'Approved' WHERE user_id = {} AND book_id = {};".format(user_id, book_id)
        query2 = "UPDATE library_user SET  reservations_approved = reservations_approved + 1 WHERE user_id = {};".format(operator_id)
        
        print(query)
        cur = db.connection.cursor()
        cur.execute(query)
        db.connection.commit()
        cur.close()

        cur2 = db.connection.cursor()
        cur2.execute(query2)
        db.connection.commit()
        cur.close()

        print(query2)

    uid = request.cookies.get('id')
    if uid == None:
        return render_template('noaccess.html')
    uid = int(uid)
    if not is_operator(uid):
        return render_template('noaccess.html')
    
    querySID = "SELECT school_id FROM library_user WHERE user_id = {};".format(operator_id) #which school am i in?
    cur2 = db.connection.cursor()
    cur2.execute(querySID)
    rv2 = cur2.fetchall()
    rv2=list(rv2)
    rv2 = rv2[0][0]
    print(rv2)
    

    query = "SELECT * FROM school_reservations WHERE approve_status = 'Pending' AND school_id = {};".format(rv2)
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()

    res = list(rv)


    

    return render_template('new_reservations.html', bookReservation = res)
    