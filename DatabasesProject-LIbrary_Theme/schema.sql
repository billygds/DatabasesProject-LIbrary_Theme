SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

DROP SCHEMA IF EXISTS library;
CREATE SCHEMA library;
SHOW WARNINGS;
USE library;
SHOW WARNINGS;
--
-- Table structure for table `school`
--

DROP TABLE IF EXISTS school;
CREATE TABLE IF NOT EXISTS school(
  school_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  school_name VARCHAR(45) NOT NULL,
  postal_code CHAR(5) NOT NULL,
  city VARCHAR(20) NOT NULL,
  phone CHAR(10) NOT NULL,
  email VARCHAR(45) NOT NULL,
  principal_name VARCHAR(45) NOT NULL,
  operator_name VARCHAR(45) NOT NULL,
  last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (school_id)
) ENGINE=InnoDB;

SHOW WARNINGS;
CREATE TABLE IF NOT EXISTS book (
  book_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  ISBN CHAR(11) NOT NULL, 
  title VARCHAR(45) NOT NULL,
  publisher VARCHAR(45) NOT NULL, 
  writer VARCHAR(45) NOT NULL,
  num_of_pages INT UNSIGNED NOT NULL,
  summary VARCHAR(1024) NOT NULL,
  language_of_book VARCHAR(15) NOT NULL,
  PRIMARY KEY (book_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


SHOW WARNINGS;
CREATE TABLE IF NOT EXISTS administrator(
  administrator_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  administrator_username VARCHAR(50),
  administrator_password VARCHAR(50),
  administrator_name VARCHAR(15) NOT NULL,
  administrator_surname VARCHAR(15) NOT NULL,
  administrator_age INT UNSIGNED NOT NULL,
  administrator_phone CHAR(10),
  administrator_postal_code CHAR(5),
  administrator_email VARCHAR(45) NOT NULL,
  administrator_sex ENUM('M','F','NB') NOT NULL,
  PRIMARY KEY(administrator_id),
  CONSTRAINT unique_row_constraint UNIQUE (administrator_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create the 'library_user' table
CREATE TABLE IF NOT EXISTS library_user (
  user_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  username VARCHAR(50),
  user_password VARCHAR(50),
  user_name VARCHAR(50),
  user_surname VARCHAR(50),
  user_email VARCHAR(50),
  operator_postal_code CHAR(5),
  phone CHAR(10),
  user_age VARCHAR(50),
  user_sex VARCHAR(50),
  user_class VARCHAR(50),
  user_type ENUM('student', 'professor') NOT NULL,
  is_operator BOOLEAN NOT NULL DEFAULT FALSE,
  able_status ENUM('new', 'OK', 'disabled') NOT NULL DEFAULT 'OK',
  school_id INT UNSIGNED, 
  borrows_approved INT UNSIGNED NOT NULL DEFAULT 0,
  reviews_approved INT UNSIGNED NOT NULL DEFAULT 0,
  reservations_approved INT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id),
  CONSTRAINT fk_school_id FOREIGN KEY (school_id) REFERENCES school(school_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_is_operator CHECK (user_type = 'professor' OR is_operator = FALSE)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS author(
  author_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  author_name VARCHAR(20) NOT NULL,
  PRIMARY KEY (author_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS category(
  category_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  category_name VARCHAR(50) NOT NULL,
  PRIMARY KEY (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS keyword(
  keyword_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  key_word VARCHAR(20) NOT NULL,
  PRIMARY KEY (keyword_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;



-------------------------------------
-- Connection tables from here and on

SHOW WARNINGS;
CREATE TABLE IF NOT EXISTS wrote (
  author_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  book_id INT UNSIGNED NOT NULL,
  PRIMARY KEY (author_id, book_id),
  CONSTRAINT fk_book_has_author1 FOREIGN KEY (author_id) REFERENCES author(author_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_book_has_author2 FOREIGN KEY (book_id) REFERENCES book(book_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS has_category (
  category_id INT UNSIGNED NOT NULL,
  book_id INT UNSIGNED NOT NULL,
  PRIMARY KEY (category_id, book_id),
  CONSTRAINT fk_book_has_category1
    FOREIGN KEY (category_id)
    REFERENCES category (category_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_book_has_category2
    FOREIGN KEY (book_id)
    REFERENCES book (book_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS has_keyword (
  keyword_id INT UNSIGNED NOT NULL,
  book_id INT UNSIGNED NOT NULL,
  PRIMARY KEY (keyword_id, book_id),
  CONSTRAINT fk_book_has_keyword1
    FOREIGN KEY (keyword_id)
    REFERENCES keyword (keyword_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_book_has_keyword2
    FOREIGN KEY (book_id)
    REFERENCES book (book_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
  
)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS borrows (
  user_id INT UNSIGNED NOT NULL,
  book_id INT UNSIGNED NOT NULL,
  date_of_borrow DATE NOT NULL,
  approve_status ENUM('Pending', 'Approved', 'Overdue', 'Returned') NOT NULL DEFAULT 'Pending',
  PRIMARY KEY (user_id, book_id),
  CONSTRAINT fk_user_borrows
    FOREIGN KEY (user_id)
    REFERENCES library_user (user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_user_borrows2
    FOREIGN KEY (book_id)
    REFERENCES book (book_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS returned (
  user_id INT UNSIGNED NOT NULL,
  book_id INT UNSIGNED NOT NULL,
  date_of_return DATE NOT NULL,
  PRIMARY KEY (user_id, book_id),
  CONSTRAINT fk_user_returns
    FOREIGN KEY (user_id)
    REFERENCES library_user (user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_user_returns2
    FOREIGN KEY (book_id)
    REFERENCES book (book_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS reviews (
  user_id INT UNSIGNED NOT NULL,
  book_id INT UNSIGNED NOT NULL,
  review VARCHAR(2000) NOT NULL,
  review_score INT UNSIGNED NOT NULL,
  approve_status ENUM('Pending', 'Approved') NOT NULL DEFAULT 'Pending',
  PRIMARY KEY (user_id, book_id),
  CONSTRAINT fk_user_reviews
    FOREIGN KEY (user_id)
    REFERENCES library_user (user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_user_reviews2
    FOREIGN KEY (book_id)
    REFERENCES book (book_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS reservations (
  user_id INT UNSIGNED NOT NULL,
  book_id INT UNSIGNED NOT NULL,
  deadline_of_reservation DATE,
  approve_status ENUM('Pending', 'Approved', 'On Hold', 'Overdue') NOT NULL DEFAULT 'Pending',
  PRIMARY KEY (user_id, book_id),
  CONSTRAINT fk_user_reservations
    FOREIGN KEY (user_id)
    REFERENCES library_user (user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_user_reservations2
    FOREIGN KEY (book_id)
    REFERENCES book (book_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS contains (
  school_id INT UNSIGNED NOT NULL,
  book_id INT UNSIGNED NOT NULL,
  number_of_copies INT NOT NULL,
  PRIMARY KEY (school_id, book_id),
  CONSTRAINT
    FOREIGN KEY (school_id)
    REFERENCES school (school_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT
    FOREIGN KEY (book_id)
    REFERENCES book (book_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
)
ENGINE = InnoDB;

----------------------VIEW------------------------------
CREATE VIEW school_borrows AS
SELECT b.user_id, b.book_id, b.date_of_borrow, b.approve_status, lu.school_id
FROM borrows b
JOIN library_user lu ON b.user_id = lu.user_id;

CREATE VIEW school_reviews AS
SELECT r.user_id, r.book_id, r.review, r.review_score, r.approve_status, lu.school_id
FROM reviews r
JOIN library_user lu ON r.user_id = lu.user_id;

CREATE VIEW school_reservations AS
SELECT res.user_id, res.book_id, res.deadline_of_reservation, res.approve_status, lu.school_id
FROM reservations res
JOIN library_user lu ON res.user_id = lu.user_id;

CREATE VIEW review_categories AS
SELECT r.user_id, r.book_id, r.review, r.review_score, r.approve_status, h.category_id
FROM reviews r
JOIN has_category h ON r.book_id = h.book_id;

