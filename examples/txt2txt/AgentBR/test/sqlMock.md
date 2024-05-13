To install MySQL or SQLite on an Ubuntu server, create a sample table, and populate it with data, follow these steps:

### Step 1: Install MySQL (Optional)

If you prefer to use MySQL instead of SQLite, you can install it using the following commands:

```sh
sudo apt update
sudo apt install mysql-server
```

After installation, secure your MySQL installation:

```sh
sudo mysql_secure_installation
```

You will be prompted to configure security options, including setting a password for the root user.

### Step 2: Install SQLite

SQLite is usually pre-installed on Ubuntu. You can check if it's installed with:

```sh
sqlite3 --version
```

If it's not installed, you can install it using:

```sh
sudo apt update
sudo apt install sqlite3 libsqlite3-dev
```

### Step 3: Create Database and Table

#### For MySQL:

Log in to the MySQL server with the root user (or any other administrative user):

```sh
sudo mysql -u root -p
```

Create a new database and user (optional):

```sql
CREATE DATABASE test_db;
CREATE USER 'test_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON test_db.* TO 'test_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Log in as the new user:

```sh
mysql -u test_user -p
```

Select the database and create a table:

```sql
USE test_db;

CREATE TABLE demo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    column1 VARCHAR(255),
    column2 VARCHAR(255),
    column3 VARCHAR(255),
    column4 VARCHAR(255),
    column5 VARCHAR(255)
);
```

Populate the table with 100 items (this is a simple example; you'd replace the values with your own):

```sql
INSERT INTO demo (column1, column2, column3, column4, column5)
VALUES ('value1', 'value2', 'value3', 'value4', 'value5');
```

Check the table to verify the data:

```sql
SELECT * FROM demo;
+----+---------+---------+---------+---------+---------+
| id | column1 | column2 | column3 | column4 | column5 |
+----+---------+---------+---------+---------+---------+
|  1 | value1  | value2  | value3  | value4  | value5  |
+----+---------+---------+---------+---------+---------+
1 row in set (0.00 sec)
```

You would need to repeat the `INSERT` statement or write a script to insert 100 rows.

#### For SQLite:

Create a new SQLite database and table:

```sh
sqlite3 test_db.db
```

Within the SQLite prompt, create a table:

```sql
CREATE TABLE demo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    column1 TEXT,
    column2 TEXT,
    column3 TEXT,
    column4 TEXT,
    column5 TEXT
);
```

Populate the table with 100 items (you can use a script or manually insert them):

```sql
INSERT INTO demo (column1, column2, column3, column4, column5)
VALUES ('value1', 'value2', 'value3', 'value4', 'value5');
```

Exit SQLite:

```sql
.quit
```

### Step 4: Use the Database in Python

For MySQL, you would use a connection string like `"mysql+pymysql://test_user:password@localhost/test_db"`.

For SQLite, as in your example, the connection string for an SQLite database would be `"sqlite:///test_db.db"` if the database file is in the same directory as your script.

Here's how you would use the SQLite database in Python:

```python
from langchain_community.utilities import SQLDatabase

# Make sure the path to the SQLite database is correct
db = SQLDatabase.from_uri("sqlite:///test_db.db")
```

If you installed MySQL and wish to use it, you would need to ensure you have a MySQL driver installed in Python (like `pymysql` or `mysql-connector-python`) and use the proper connection string.

### Step 5: Install Python Driver for MySQL (If using MySQL)

For MySQL, you'll need a Python driver to connect to the database. You can install `pymysql` with:

```sh
pip install pymysql
```

Then, you can use it in Python like this:

```python
from langchain_community.utilities import SQLDatabase

# Update the username, password, and database name accordingly
db = SQLDatabase.from_uri("mysql+pymysql://test_user:password@localhost/test_db")
```

Remember to replace `test_user`, `password`, and `test_db` with the actual MySQL username, password, and database name you set up earlier.

The output for our example would be:

```python
>>> from langchain_community.utilities import SQLDatabase
>>> db = SQLDatabase.from_uri("mysql+pymysql://test_user:password@localhost/test_db")
>>> db.get_table_info()
'\nCREATE TABLE demo (\n\tid INTEGER NOT NULL AUTO_INCREMENT, \n\tcolumn1 VARCHAR(255), \n\tcolumn2 VARCHAR(255), \n\tcolumn3 VARCHAR(255), \n\tcolumn4 VARCHAR(255), \n\tcolumn5 VARCHAR(255), \n\tPRIMARY KEY (id)\n)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_0900_ai_ci\n\n/*\n3 rows from demo table:\nid\tcolumn1\tcolumn2\tcolumn3\tcolumn4\tcolumn5\n1\tvalue1\tvalue2\tvalue3\tvalue4\tvalue5\n*/'
>>>

remove the leading and trailing '\n' characters from the output string.
CREATE TABLE demo (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    column1 VARCHAR(255), 
    column2 VARCHAR(255), 
    column3 VARCHAR(255), 
    column4 VARCHAR(255), 
    column5 VARCHAR(255), 
    PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_0900_ai_ci

/*
3 rows from demo table:
id  column1  column2  column3  column4  column5
1   value1   value2   value3   value4   value5
*/
```

### Note:
- The `langchain_community.utilities.SQLDatabase` class used in your example is not a standard Python library. Ensure that this module is available in your environment and it supports the databases you are working with.
- Always secure your database credentials and avoid hardcoding them into your code. Use environment variables or configuration files for better security practices.