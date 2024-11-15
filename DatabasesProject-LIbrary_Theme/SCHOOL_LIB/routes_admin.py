from flask import Flask, render_template, request, make_response, flash, redirect, url_for, abort, jsonify
from flask_mysqldb import MySQL
from SCHOOL_LIB import app, db ## initially created by __init__.py, need to be used here
import json
from collections import Counter

from flask import request

@app.route("/admin1", methods=["GET", "POST"])
def available_admin1():
    year = 2022
    month = 1
    if request.method == "POST": 
        print('debug1')
        month = request.form['month']
        year = request.form['year']
        print(month)
        print(year)
        # we have to query the database for the selected month, year
    
    query = '''
    SELECT s.school_id, s.school_name, COUNT(b.user_id) AS borrow_count
    FROM school s
    JOIN library_user u ON s.school_id = u.school_id
    JOIN borrows b ON u.user_id = b.user_id
    WHERE YEAR(b.date_of_borrow) = {} AND MONTH(b.date_of_borrow) = {}
    GROUP BY s.school_id, s.school_name;
    '''.format(year, month)

    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()

    return render_template("adminPage1.html", school_borrows=rv)





@app.route("/admin2", methods=["GET"])
def admin2():
    id = request.cookies.get('id')
    if id != 'admin':
        return render_template('noaccess.html')
    # Retrieve all categories from the database
    category_query = "SELECT DISTINCT category_name FROM category;"
    cur = db.connection.cursor()
    cur.execute(category_query)
    categories = [row[0] for row in cur.fetchall()]
    cur.close()

    # Check if a category is selected by the user
    chosen_category = request.args.get('category')

    if chosen_category:
        # Query to fetch the writers and professor names based on the chosen category
        writer_query = '''
        SELECT DISTINCT b.writer
        FROM book b
        JOIN has_category hc ON b.book_id = hc.book_id
        JOIN category c ON hc.category_id = c.category_id
        WHERE c.category_name = %s;
        '''

        professor_query = '''
        SELECT DISTINCT lu.user_name, lu.user_surname
        FROM library_user lu
        JOIN borrows br ON lu.user_id = br.user_id
        JOIN book b ON br.book_id = b.book_id
        JOIN has_category hc ON b.book_id = hc.book_id
        JOIN category c ON hc.category_id = c.category_id
        WHERE c.category_name = %s
          AND lu.user_type = 'professor'
          AND br.date_of_borrow >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR);
        '''

        cur = db.connection.cursor()
        cur.execute(writer_query, (chosen_category,))
        writers = [row[0] for row in cur.fetchall()]

        print("Chosen Category:", chosen_category)
        print("Writers:", writers)

        cur.execute(professor_query, (chosen_category,))
        professor_results = cur.fetchall()
        professors = [(professor[0], professor[1]) for professor in professor_results]

        print("Professors Query:")
        print(professor_query)
        print("Professors:", professors)

        cur.close()

        return render_template("adminPage2.html", writers=writers, professors=professors, categories=categories, chosen_category=chosen_category)
    else:
        return render_template("adminPage2.html", categories=categories)


@app.route("/admin3")
def admin3():
    id = request.cookies.get('id')
    if id != 'admin':
        return render_template('noaccess.html')
    query = '''
    SELECT lu.user_name, lu.user_surname, COUNT(b.book_id) AS borrowed_books
    FROM library_user lu
    JOIN borrows br ON lu.user_id = br.user_id
    JOIN book b ON br.book_id = b.book_id
    WHERE lu.user_type = 'professor' AND lu.user_age < 40
    GROUP BY lu.user_id
    ORDER BY borrowed_books DESC;
    '''

    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()
    print (rv)
    professor_books = [(row[0] + ' ' + row[1], row[2]) for row in rv]  # Extracting professor IDs and borrowed book counts
    
    return render_template("adminPage3.html", professor_books=professor_books)

@app.route("/admin4")
def available_admin4():
    id = request.cookies.get('id')
    if id != 'admin':
        return render_template('noaccess.html')
    query = '''
    SELECT DISTINCT b.writer
    FROM book b
    LEFT JOIN borrows br ON b.book_id = br.book_id
    WHERE br.book_id IS NULL;
    '''

    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()
   
    return render_template('adminPage4.html', writers=rv)

@app.route("/admin5")
def available_admin5():
    id = request.cookies.get('id')
    if id != 'admin':
        return render_template('noaccess.html')
    query = '''
   SELECT lu.borrows_approved, lu.user_name
FROM library_user lu
WHERE lu.is_operator = 1
  AND lu.borrows_approved > 5
  AND lu.borrows_approved IN (
    SELECT lu2.borrows_approved
    FROM borrows b
    JOIN library_user lu2 ON b.user_id = lu2.user_id
    WHERE lu2.is_operator = 1
      AND b.date_of_borrow >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
    GROUP BY lu2.borrows_approved
    HAVING COUNT(*) > 1
  );

    '''
   
    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()
    print(rv)
    print (list(rv))
    return render_template('adminPage5.html', operatorData=rv)

@app.route("/admin6")
def admin6():
    query = '''
    SELECT category_combination, combination_count
FROM (
    SELECT category_combination, COUNT(*) AS combination_count
    FROM (
        SELECT GROUP_CONCAT(DISTINCT c.category_name ORDER BY c.category_name SEPARATOR ',') AS category_combination
        FROM book b
        JOIN has_category hc ON b.book_id = hc.book_id
        JOIN category c ON hc.category_id = c.category_id
        JOIN borrows br ON b.book_id = br.book_id
        GROUP BY b.book_id
        HAVING COUNT(DISTINCT c.category_name) > 1
    ) AS subquery
    GROUP BY category_combination
    ORDER BY combination_count DESC
    LIMIT 3
) AS top_combinations;

    '''

    cur = db.connection.cursor()
    cur.execute(query)
    rv = cur.fetchall()

    combinations = [(index + 1, row[0], row[1]) for index, row in enumerate(rv)]

    return render_template("adminPage6.html", combinations=combinations)






@app.route("/admin7")
def admin7():
    id = request.cookies.get('id')
    if id != 'admin':
        return render_template('noaccess.html')
    # Retrieve all writers and their book counts from the database
    writer_query = "SELECT writer FROM book;"
    cur = db.connection.cursor()
    cur.execute(writer_query)
    writers = [row[0] for row in cur.fetchall()]
    cur.close()

    # Count the number of books for each writer
    writer_counts = dict(Counter(writers))

    # Find the maximum book count
    max_count = max(writer_counts.values())

    # Find the threshold for including writers (at least 5 books less than the maximum)
    threshold = max_count - 5

    # Filter the writers who have written at least 5 books less than the maximum
    selected_writers = [writer for writer, count in writer_counts.items() if count >= threshold and count != max_count]

    return render_template("adminPage7.html", writers=selected_writers)




   


