
from unicodedata import category
from unittest import result
from flask import Flask, render_template, request,redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ORSFinal1'

mysql = MySQL(app)
@app.route("/customer", methods=["POST", "GET"])

    
        
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method=='GET':
        return render_template("index.html")
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        # Fetch form data
        print(request.form)
        username = request.form["username"]
        password = request.form["password"]
        typeOf = request.form["typeOf"]
        if (typeOf == "Customer"):
            cur.execute('SELECT * from ors WHERE type= "Customer" AND username =%s AND Password= %s' , (username ,password))
            myresult = cur.fetchall()
            if (myresult):
                    return redirect(url_for("ProductPage"))
            return redirect(url_for("index"))

        elif (typeOf == "Vendor"):
            cur.execute('SELECT * from ors WHERE Usertype ="Vendor" AND Username = %s AND Password = %s', (username, password))
            myresult = cur.fetchall()
            if (myresult):
                # temp = typeOf[0] + username
                # if (temp == password):
                #     session.permanent = True
                #     session["user"] = myresult[0]
                    return redirect(url_for("vendor"))
            return redirect(url_for("index"))
        else:
            return redirect(url_for("index"))
# SELECT * 
@app.route('/user')
def users():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM ORS")
    if resultValue > 0:
        userDetails = cur.fetchall()
        return render_template('user.html',userDetails=userDetails)

@app.route('/NewCustomer' , methods=['POST', 'GET'])
def NewCustomer():
    if( request.method=='GET'):
       return render_template("NewCustomer.html") 
    if request.method=='POST':
        userDetails1 = request.form
        name = userDetails1['name']
        email = userDetails1['email']
        phone = userDetails1['contact']
        age = userDetails1['age']
        cur = mysql.connection.cursor()
        cur.execute("SELECT MAX(CustomerID) From Customer;")
        result = (cur.fetchall()) 
        for r in result:
            id = r[0]
        try:
            cur.execute("INSERT INTO Customer(CustomerID, Name, Email,contact,age) VALUES(%s,%s,%s,%s,%s)" , (id+1,name, email,phone,age))
            mysql.connection.commit()
        except:
            return redirect(url_for("index"))
        cur.close()
        return redirect(url_for("NewCustomer.html"))
    return render_template('NewCustomer.html')


@app.route('/ConfirmCustomer')
def Confirm():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM Customer")
    if resultValue > 0:
        userDetails1 = cur.fetchall()
        return render_template('ConfirmCustomer.html',userDetails1=userDetails1)
@app.route('/ProductPage', methods=['POST', 'GET'])
def ProductPage():
    if request.method=='GET':

        cur = mysql.connection.cursor()
        cur.execute("SELECT distinct(Type) from ProductList")
        myresult = cur.fetchall()
        x=[]
        for i in myresult:
            x.append(i[0])
        return render_template("ProductPage.html", x=x) 

    if request.method=='POST':
       userDetails = request.form  

       category = userDetails['Category']
       
       L=[]
       L.append(category)
       cur = mysql.connection.cursor()
       q = "SELECT * FROM ProductList WHERE Type = %s " 
       cur.execute(q, L)
       myresult = cur.fetchall()
      
        
       return render_template("Product.html",x=myresult)


       
if __name__ == '__main__':
    app.run(debug=True,port = 50001)