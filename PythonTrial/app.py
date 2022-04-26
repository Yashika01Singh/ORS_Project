from unittest import result
from flask import Flask, render_template, request,redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ORSFinal1'

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method=='GET':
        return render_template("index.html")
    if request.method == 'POST':
        # Fetch form data
        userDetails = request.form
        name = userDetails['name']
        email = userDetails['email']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO ORS(name, email) VALUES(%s, %s)",(name, email))
        mysql.connection.commit()
        cur.close()
        return redirect('/user')
        # return redirect('/NewCustomer')
    return redirect(url_for('index.html'))

@app.route('/user')
def users():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM ORS")
    if resultValue > 0:
        userDetails = cur.fetchall()
        return render_template('user.html',userDetails=userDetails)

@app.route('/NewCustomer')
def NewCustomer():
    if request.method=='POST':
        userDetails1 = request.form;
        name = userDetails1['name']
        email = userDetails1['email']
        phone = userDetails1['contact']
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) from Customer")
        result = cur.fetchall()
        cur.execute("INSERT INTO Customer(CustomerID, Name, Email,contact) VALUES(%s,%s,%s,%s)" , (result+1,name, email,phone))
        mysql.connection.commit();
        cur.close()
        return redirect('/NewCustomer')
    return render_template('NewCustomer.html')


@app.route('/ConfirmCustomer')
def Confirm():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM Customer")
    if resultValue > 0:
        userDetails1 = cur.fetchall()
        return render_template('ConfirmCustomer.html',userDetails1=userDetails1)
@app.route('/ProductPage')
def ProductPage():
    return render_template('ProductPage.html')   
if __name__ == '__main__':
    app.run(debug=True,port = 50001)