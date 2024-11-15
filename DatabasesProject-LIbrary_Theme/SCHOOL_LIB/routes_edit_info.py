from flask import Flask, render_template, request, make_response, flash, redirect, url_for, abort, jsonify
from flask_mysqldb import MySQL
from SCHOOL_LIB import app, db ## initially created by __init__.py, need to be used here
import json

@app.route('/edit_info')
def edit_info():
    id = int(request.cookies.get('id'))
    query = "SELECT * FROM {} WHERE user_id = '{}';".format('library_user', id)
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()
    user = [item for sublist in rv for item in sublist]
    print(user)
    if user[11] == 'student':
        return render_template('edit_info_std.html', user = user)
    else:
        return render_template('edit_info.html', user = user)
    
@app.route('/save_info', methods = ['POST'])
def save_info():
    id = int(request.cookies.get('id'))
    username = request.form['username']
    password = request.form['password']
    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']
    sex = request.form['sex']
    age = request.form['age']
    uclass = request.form['class']

    # update database
    # show /dashboard
    query = "UPDATE library_user SET username = '{}', user_password = '{}', user_email = '{}', user_class = '{}', user_name = '{}', user_surname = '{}', user_age = {}, user_sex = '{}' WHERE user_id = {};".format(username, password, email, uclass, name, surname, age, sex, id)
    print(query)
    cur = db.connection.cursor()
    cur.execute(query)
    db.connection.commit()
    cur.close()

    query = "SELECT * FROM {} WHERE user_id = '{}';".format('library_user', id)
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()
    user = [item for sublist in rv for item in sublist]
    print(user)
    if user[11] == 'student':
        return render_template('dashboardStd.html', user = user)
    else:
        if user[11] == 'professor':
            print("I am a Professor")
            query = '''SELECT is_operator
                    FROM library_user
                    WHERE user_name = '{}' AND user_surname = '{}';'''.format(user[3], user[4])
           
            cur = db.connection.cursor()
            cur.execute(query)
            rv = cur.fetchall()
            
            print(rv)
            isOperator = rv[0][0]  # 1 if Operator - 0 if not Operator
            if isOperator == 1:
                print("I am a Professor and an Operator")
                webpage = render_template("dashboardOp.html", user = user)
                resp = make_response(webpage)
                resp.set_cookie('id', str(user[0]))
                return resp
            else:
                webpage = render_template("dashboardProf.html", user = user)
                resp = make_response(webpage)
                resp.set_cookie('id', str(user[0]))
                return resp




@app.route('/editBook', methods=['POST'])
def editBook():
    book_id = request.form['book_id']
    query = "SELECT * FROM book WHERE book_id = %s;"
    cur = db.connection.cursor()
    cur.execute(query, (book_id,))
    book = cur.fetchone()
    cur.close()

    if book[5] == 'student':
        return render_template('edit_info_std.html', book=book)
    else:
        return render_template('edit_info_book.html', book=book)
    
    
    
@app.route('/save_book_info', methods = ['POST'])
def save_book_info():
    id = int(request.cookies.get('id'))
    book_id = request.form ['id']
    ISBN = request.form['ISBN']
    Title = request.form['Title']
    Publisher = request.form['Publisher']
    Writer = request.form['Writer']
    Summary = request.form['Summary']
    # update database
    # show /dashboard
    query = "UPDATE book SET ISBN = '{}', Title = '{}', Publisher = '{}', Writer = '{}', Summary = '{}' WHERE book_id = {};".format(ISBN, Title, Publisher, Writer, Summary, book_id)
    print(query)
    cur = db.connection.cursor()
    cur.execute(query)
    db.connection.commit()
    cur.close()

    query = "SELECT * FROM {} WHERE book_id = '{}';".format('book', id)
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()
    user = [item for sublist in rv for item in sublist]
    print(user)        
    if user[5] == 'student':
        return render_template('dashboardStd.html', user = user)
    else:
        
            print("I am a Professor")
            query = '''SELECT is_operator
                    FROM library_user
                    WHERE user_name = '{}' AND user_surname = '{}';'''.format(user[3], user[4])
           
            cur = db.connection.cursor()
            cur.execute(query)
            rv = cur.fetchall()
            
            print(rv)
           
            print("I am a Professor and an Operator")
            webpage = render_template("dashboardOp.html", user = user)
            resp = make_response(webpage)
            resp.set_cookie('id', str(user[0]))
            return resp

