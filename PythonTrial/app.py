
from unicodedata import category
from unittest import result
from flask import Flask, render_template, request,redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "ORS"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Yashika@123'
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
                    session["user"] = myresult[0]
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

       category = userDetails["Category"]
       
       L=[]
       L.append(category)
       cur = mysql.connection.cursor()
       q = "SELECT * FROM ProductList WHERE Type = %s " 
       cur.execute(q, L)
       myresult = cur.fetchall()
      
        
       return render_template("Product.html",x=myresult)

@app.route('/Product', methods=['POST', 'GET'])
def Product():
    if request.method=='GET':
        return render_template("Product.html") 

    if request.method=='POST':
       userDetails1 = request.form  

       Product = userDetails1["Product"]     
        
       return render_template("Product.html")
@app.route('/Order', methods=['POST', 'GET'])
def Order():     
    if( request.method=='GET'):
       return render_template("Order.html") 
    if request.method=='POST':
        Price = 0
        Discount=0
        VendorID=0
        userDetails1 = request.form
        ProductID = userDetails1['ProductID']
        Quantity = userDetails1['Quantity']
        cur = mysql.connection.cursor()
        cur.execute("SELECT MAX(CartID) From cart;")
        result = cur.fetchall() 
        for r in result:
            cartid = r[0]
        cartid+=1
        cur.execute(f"SELECT Price from ProductInventory where ProductID='{ProductID}'")
        result = cur.fetchall()
        for r in result:
            Price = r[0]
        cur.execute(f"SELECT Discount from ProductInventory where ProductID='{ProductID}'")
        result = cur.fetchall()
        for r in result:
            Discount = r[0]
        CustomerID = session.get("user")[0]
        cur.execute(f"SELECT VendorID from ProductInventory where ProductID='{ProductID}'")
        result = cur.fetchall()
        for r in result:
            VendorID = r[0]
        cur.execute("SELECT MAX(OrderID) from Orders")
        result = cur.fetchall()
        for r in result:
            OrderID = r[0]
        OrderID+=1
        cur.execute("SET FOREIGN_KEY_CHECKS=0")
        q="INSERT INTO Orders(CustomerID,OrderID,ProductID,VendorID,Amount,Quantity,Status,OrderDate,ExpectedDeliveryDate) VALUES (%s,%s,%s,%s,%s,%s,'Active','2022-04-23','2022-05-21');"
        cur.execute(q,(CustomerID,OrderID,ProductID,VendorID,Price,Quantity))
        mysql.connection.commit()
        
        cur.close()
        return redirect(url_for("Product"))
    return render_template('Order.html')
@app.route("/customer/orders", methods=["POST" , "GET"])
def customerorder():
    cur = mysql.connection.cursor()
    if "user" in session:
        CustomerID = session.get("user")[0]
        
        cur.execute(f"SELECT * from Orders where CustomerID='{CustomerID}'")
        myresult = cur.fetchall()

        return render_template("customerOrders.html" , x = myresult)
    else: 
        return redirect(url_for("customer"))
@app.route("/customer/profile" , methods=["POST" , "GET"])
def customerProfile():
    cur = mysql.connection.cursor();
    cus= mysql.connection.cursor();

    if "user" in session : 
        CustomerID = session.get("user")[0]
        cus.execute(f"SELECT z.ModeOfPayment , z.Cardno  , z.ExpiryDateYear from CustomerPaymentMethod as z where z.CustomerID = '{CustomerID}'")
        cur.execute(f"SELECT  o.CustomerID ,o.OrderID,  o.Amount, v.Vendorname, o.Status from Orders as o , ProductList as p, Vendor as v, Customer as c where o.VendorID = v.VendorID and o.Status = 'Active' and o.CustomerID ='{CustomerID}'")
        myresult = cur.fetchall();
        myresult1 = cus.fetchall();
        return render_template("customerProfile.html" , x = myresult , y = myresult1)
        
    else:
        return redirect(url_for("customer"))       
if __name__ == '__main__':
    
    app.run(debug=True,port = 50001)