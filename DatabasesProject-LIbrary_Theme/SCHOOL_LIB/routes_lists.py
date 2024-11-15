from flask import Flask, render_template, request, make_response, flash, redirect, url_for, abort, jsonify
from flask_mysqldb import MySQL
from SCHOOL_LIB import app, db ## initially created by __init__.py, need to be used here
import json

@app.route("/schools")
def schools():
    table = 'school'
    query = "SELECT * FROM {};".format(table)
    
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()
    cur.close()
    schools=list(rv)
    
    return render_template('schools.html', schools=schools)

@app.route("/users")
def students():
    table = 'library_user'
    query = "SELECT * FROM {};".format(table)
    
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()
    return str(rv)

@app.route("/books")
def books():
    id = request.cookies.get('id')
    usr = db.connection.cursor()
    if id != 'admin':
        print(id)
        usr.execute("SELECT * FROM library_user WHERE user_id = {};".format(id))
        currentUser = usr.fetchall()
        currentUser = list(currentUser)
        print(currentUser)

    table = 'book'
    query = """SELECT b.*, GROUP_CONCAT(c.category_name) AS categories
            FROM book b
            JOIN has_category hc ON b.book_id = hc.book_id
            JOIN category c ON hc.category_id = c.category_id
            GROUP BY b.book_id;""".format(table)
    ####
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()
    bookList = list(rv)
    # print(bookList)
    # booklist has this form
    # book_id
    # ISBN
    # title
    # publisher
    # writer
    # num_of_pages
    # summary
    # num_of_copies
    # language_of_book
    # categories
    
    query2 = "SELECT * FROM school WHERE school_id = {};".format(currentUser[0][14])
    scl = db.connection.cursor()
    scl.execute(query2)
    school = scl.fetchall()
    school = list(school)

    query3 = '''
                SELECT b.book_id, b.ISBN, b.title, b.publisher, b.writer, b.num_of_pages, b.summary, scb.number_of_copies, b.language_of_book, GROUP_CONCAT(c.category_name) AS categories
                FROM school AS s
                JOIN library_user AS lu ON lu.school_id = s.school_id
                JOIN contains AS scb ON s.school_id = scb.school_id
                JOIN book AS b ON scb.book_id = b.book_id
                
                JOIN has_category hc ON b.book_id = hc.book_id
                JOIN category c ON hc.category_id = c.category_id
                WHERE lu.user_id = {}
                GROUP BY b.book_id;
            '''.format(id)
    cur = db.connection.cursor()
    cur.execute(query3)
    rv = cur.fetchall()
    print('Hello Barbie')
    rv = list(rv)

    if currentUser[0][12] == 1:
        print('mamamou')
        return render_template("bookListOP.html", books=rv, user=currentUser, school = school)
    
    return render_template("bookList.html", books=rv, user=currentUser, school = school)

@app.route("/books/borrowed")
def booksBorrowed():
    id = request.cookies.get('id')
    usr = db.connection.cursor()
    usr.execute("SELECT * FROM library_user WHERE user_id = {};".format(id))
    currentUser = usr.fetchall()
    currentUser = list(currentUser)
    print(currentUser)


    table = 'book'
    query = """SELECT b.*, GROUP_CONCAT(c.category_name) AS categories
            FROM book b
            JOIN has_category hc ON b.book_id = hc.book_id
            JOIN category c ON hc.category_id = c.category_id
            GROUP BY b.book_id;""".format(table)
    
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()
    bookList = list(rv)
    
    
    query2 = "SELECT * FROM school WHERE school_id = {};".format(currentUser[0][14])
    scl = db.connection.cursor()
    scl.execute(query2)
    school = scl.fetchall()
    school = list(school)

    query3 = """SELECT b.*
                      FROM book b
                      JOIN borrows bor ON b.book_id = bor.book_id
                      WHERE user_id = {};
                      """.format(currentUser[0][0])

    borrows_cur = db.connection.cursor()
    borrows_cur.execute(query3)
    borrowed_books = borrows_cur.fetchall()
    borrowed_books = list(borrowed_books)
    print(borrowed_books)


    return render_template("bookList.html", books=borrowed_books, user=currentUser, school = school)
    
@app.route("/books/<string:book_id>", methods=["GET"])
def bookView(book_id):
    query = """SELECT b.*, GROUP_CONCAT(c.category_name) AS categories
            FROM book b
            JOIN has_category hc ON b.book_id = hc.book_id
            JOIN category c ON hc.category_id = c.category_id
            WHERE b.book_id = {}
            GROUP BY b.book_id;""".format(book_id)
    print(query)
    print("check1")
    cur = db.connection.cursor()
    print("check111")
    cur.execute(query)
    print("check222")
    rv = cur.fetchall()
    print("check2")
    bookDetails = list(rv[0])
    print(bookDetails)
    return render_template("bookPage.html", bookDetails = bookDetails)

@app.route("/books/<string:book_id>/borrow", methods=["POST"])
def bookBorrow(book_id):
    id = request.cookies.get('id')

    usr = db.connection.cursor()
    usr.execute("SELECT * FROM library_user WHERE user_id = {};".format(id))
    currentUser = usr.fetchall()
    currentUser = list(currentUser)

    limit = """SELECT COUNT(*) AS borrow_count
        FROM borrows
        WHERE user_id = {};""".format(id)
    
    lm = db.connection.cursor()
    lm.execute(limit)
    totalBorrows = lm.fetchall()
    totalBorrows = list(totalBorrows)
    print(totalBorrows)

    #Check Borrow Limit
    if totalBorrows[0][0] >=2:
        return render_template("limitReached.html", borrowCount = totalBorrows[0][0])
    
    if totalBorrows[0][0] >=1 and currentUser[0][11] == 'professor':
        return render_template("limitReached.html", borrowCount = totalBorrows[0][0])
    
    Capacity = """SELECT number_of_copies
                FROM contains
                WHERE book_id = {} AND school_id = {};""".format(book_id, currentUser[0][14])
    
    cp = db.connection.cursor()
    cp.execute(Capacity)
    copiesLeft = cp.fetchall()
    copiesLeft = list(copiesLeft)
    print(copiesLeft)

    Title = request.form['book_title']

    if copiesLeft[0][0] == 0:
        return render_template("bookDepleted.html", bookTitle = Title)
    
    
    
    
    query = '''INSERT INTO borrows(user_id, book_id, date_of_borrow) VALUES ({}, {}, CURDATE())'''.format(id, book_id)

    br = db.connection.cursor()
    br.execute(query)
    db.connection.commit()
    br.close()
    print(query)
    print(currentUser[0][11], ' ------------------', currentUser[0][12])
    return redirect('/dashboard')
    

@app.route("/books/<string:book_id>/reserve", methods=["POST"])
def bookReserve(book_id):
    id = request.cookies.get('id')

    usr = db.connection.cursor()
    usr.execute("SELECT * FROM library_user WHERE user_id = {};".format(id))
    currentUser = usr.fetchall()
    currentUser = list(currentUser)

    Capacity = """SELECT number_of_copies
                FROM contains
                WHERE book_id = {} AND school_id = {};""".format(book_id, currentUser[0][14])
    
    cp = db.connection.cursor()
    cp.execute(Capacity)
    copiesLeft = cp.fetchall()
    copiesLeft = list(copiesLeft)

    Title = request.form['book_title']

    if copiesLeft[0][0] == 0:
        return render_template("bookDepleted.html", bookTitle = Title)
    
    Reservations = """SELECT COUNT(*) AS reservation_count
                    FROM reservations
                    WHERE user_id = {};""".format(id)
    res = db.connection.cursor()
    res.execute(Reservations)
    userRes = res.fetchall()
    userRes = list(userRes)
    print(userRes)

    if (userRes[0][0] >= 2 and currentUser[0][11] == 'student') or (userRes[0][0] >= 1 and currentUser[0][11] == 'professor'):
        return render_template("limitReached.html", borrowCount = userRes[0][0])

    query = '''INSERT INTO reservations(user_id, book_id, deadline_of_reservation) VALUES ({}, {}, DATE_ADD(CURDATE(), INTERVAL 14 DAY))'''.format(id, book_id)

    br = db.connection.cursor()
    br.execute(query)
    db.connection.commit()
    br.close()
    print(query)
    return '1'

@app.route("/reviewBook", methods=["POST"])
def reviewBook():
    id = request.cookies.get('id')
    book_id = request.form['book_id']
    print(id)
    query = "SELECT * FROM book WHERE book_id = {};".format(book_id)

    bk = db.connection.cursor()
    bk.execute(query)
    book = bk.fetchall()
    book = list(book)
    print(book)
    return render_template("reviewPage.html", bookDetails = book, user_id = id)

@app.route("/books/<string:book_id>/review", methods=["POST"])
def bookReview(book_id):
    id = request.cookies.get('id')
    review = request.form['hidden-text']
    reviewScore = request.form['hidden-likert']
    print(review)
    print(reviewScore)
    query = '''INSERT INTO reviews(user_id, book_id, review, review_score, approve_status) VALUES ({}, {}, '{}', {}, 'Pending')'''.format(id, book_id, review, reviewScore)

    br = db.connection.cursor()
    br.execute(query)
    db.connection.commit()
    br.close()
    print(query)
    return '1'

@app.route("/books/books/<string:book_id>", methods=["GET"])  #View Borrowed Book Details
def bookView2(book_id):
    query = """SELECT b.*, GROUP_CONCAT(c.category_name) AS categories
            FROM book b
            JOIN has_category hc ON b.book_id = hc.book_id
            JOIN category c ON hc.category_id = c.category_id
            WHERE b.book_id = {}
            GROUP BY b.book_id;""".format(book_id)
    print(query)
    print("check1")
    cur = db.connection.cursor()
    print("check111")
    cur.execute(query)
    print("check222")
    rv = cur.fetchall()
    print("check2")
    bookDetails = list(rv[0])
    print(bookDetails)
    return render_template("bookPage.html", bookDetails = bookDetails)

