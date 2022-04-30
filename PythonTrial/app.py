from unicodedata import category
from unittest import result
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "ORS"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pendyala'
app.config['MYSQL_DB'] = 'ORSFinal1'

mysql = MySQL(app)


@app.route("/customer", methods=["POST", "GET"])
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template("index.html")
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        # Fetch form data
        print(request.form)
        username = request.form["username"]
        password = request.form["password"]
        typeOf = request.form["typeOf"]
        if (typeOf == "Customer"):
            cur.execute('SELECT * from ors WHERE type= "Customer" AND username =%s AND Password= %s',
                        (username, password))
            myresult = cur.fetchall()

            if (myresult):
                session["user"] = myresult[0]
                return redirect(url_for("ProductPage"))
            return redirect(url_for("index"))

        elif (typeOf == "Vendor"):
            cur.execute('SELECT * from ors WHERE Usertype ="Vendor" AND Username = %s AND Password = %s',
                        (username, password))
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
        return render_template('user.html', userDetails=userDetails)


@app.route('/NewCustomer', methods=['POST', 'GET'])
def NewCustomer():
    if (request.method == 'GET'):
        return render_template("NewCustomer.html")
    if request.method == 'POST':
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
            cur.execute("INSERT INTO Customer(CustomerID, Name, Email,contact,age) VALUES(%s,%s,%s,%s,%s)",
                        (id + 1, name, email, phone, age))
            mysql.connection.commit()
        except:
            return redirect(url_for("index"))
        cur.close()
        return redirect(url_for("ProductPage"))
    return render_template('NewCustomer.html')


@app.route('/ConfirmCustomer')
def Confirm():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM Customer")
    if resultValue > 0:
        userDetails1 = cur.fetchall()
        return render_template('ConfirmCustomer.html', userDetails1=userDetails1)


@app.route('/ProductPage', methods=['POST', 'GET'])
def ProductPage():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT distinct(Type) from ProductList")
        myresult = cur.fetchall()
        x = []
        for i in myresult:
            x.append(i[0])
        return render_template("ProductPage.html", x=x)

    if request.method == 'POST':
        userDetails = request.form

        category = userDetails["Category"]

        L = []
        L.append(category)
        cur = mysql.connection.cursor()
        q = "SELECT * FROM ProductList WHERE Type = %s "
        cur.execute(q, L)
        myresult = cur.fetchall()

        return render_template("Product.html", x=myresult)


@app.route('/Product', methods=['POST', 'GET'])
def Product():
    if request.method == 'GET':
        return render_template("Product.html")

    if request.method == 'POST':
        userDetails1 = request.form

        Product = userDetails1["Product"]

        return render_template("Product.html")


@app.route('/Order', methods=['POST', 'GET'])
def Order():
    if (request.method == 'GET'):
        return render_template("Order.html")
    if request.method == 'POST':
        Price = 0
        Discount = 0
        VendorID = 0
        userDetails1 = request.form
        ProductID = userDetails1['ProductID']
        Quantity = userDetails1['Quantity']
        cur = mysql.connection.cursor()
        cur.execute("SELECT MAX(CartID) From cart;")
        result = cur.fetchall()
        for r in result:
            cartid = r[0]
        cartid += 1
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
        OrderID += 1
        cur.execute("SET FOREIGN_KEY_CHECKS=0")
        q = "INSERT INTO Orders(CustomerID,OrderID,ProductID,VendorID,Amount,Quantity,Status,OrderDate,ExpectedDeliveryDate) VALUES (%s,%s,%s,%s,%s,%s,'Active','2022-04-23','2022-05-21');"
        cur.execute(q, (CustomerID, OrderID, ProductID, VendorID, Price, Quantity))
        mysql.connection.commit()

        cur.close()
        return redirect(url_for("Product"))
    return render_template('Order.html')


@app.route("/customer/orders", methods=["POST", "GET"])
def customerorder():
    cur = mysql.connection.cursor()
    if "user" in session:
        CustomerID = session.get("user")[0]

        cur.execute(f"SELECT * from Orders where CustomerID='{CustomerID}'")
        myresult = cur.fetchall()

        return render_template("customerOrders.html", x=myresult)
    else:
        return redirect(url_for("customer"))


@app.route("/customer/profile", methods=["POST", "GET"])
def customerProfile():
    cur = mysql.connection.cursor();
    cus = mysql.connection.cursor();

    if "user" in session:
        CustomerID = session.get("user")[0]
        cus.execute(
            f"SELECT z.ModeOfPayment , z.Cardno  , z.ExpiryDateYear from CustomerPaymentMethod as z where z.CustomerID = '{CustomerID}'")
        cur.execute(
            f"SELECT  o.CustomerID ,o.OrderID,  o.Amount, v.Vendorname, o.Status from Orders as o , ProductList as p, Vendor as v, Customer as c where o.VendorID = v.VendorID and o.Status = 'Active' and o.CustomerID ='{CustomerID}'")
        myresult = cur.fetchall();
        myresult1 = cus.fetchall();
        return render_template("customerProfile.html", x=myresult, y=myresult1)

    else:
        return redirect(url_for("customer"))


@app.route("/queries/", methods=["POST", "GET"])
def queries():
    cur = mysql.connection.cursor()
    if request.method == 'GET':
        return render_template("queries.html")
    elif request.method == "POST":
        queryno = request.form["queryno"]
        if queryno == "query1":
            cur.execute(
                f"SELECT Totalitems,Discount,Amount FROM Cart WHERE Cart.CustomerID = (SELECT CustomerID FROM( SELECT CustomerID,Amount, RANK() OVER (ORDER BY Quantity DESC) AS QuantityOrder FROM Orders) as T WHERE T.QuantityOrder=1 ) ")
            myresult = (cur.fetchall())
            return render_template("query1.html", x=myresult);
        elif queryno == "query2":
            cur.execute(
                "SELECT CustomerID,TransactionID,PaymentStatus FROM Transaction WHERE Transaction.CustomerID IN (SELECT CustomerID FROM (SELECT CustomerID, OrderID ,Amount, DENSE_RANK() OVER (ORDER BY Amount DESC) AS AmountDesc FROM Orders where Status='Active') as T WHERE AmountDesc <6)")
            myresult = (cur.fetchall())
            return render_template("query2.html", x=myresult);
        elif (queryno == "query3"):
            cur.execute(
                "SELECT VendorID, Amount_Sum, Discount_Sum ,ModeOfPayment_max , dense_rank() OVER (Order by Amount_Sum DESC) as SumAmount_rank, dense_rank() OVER (Order by Discount_Sum DESC) as SumDiscount_rank, dense_rank() OVER (Order by ModeOfPayment_max  DESC) as MaxModeOfPayment_rank FROM (SELECT VendorID, Sum(Amount) AS Amount_Sum , Sum(Discount) AS Discount_Sum ,Max(ModeOfPayment) AS ModeOfPayment_max  FROM (SELECT* FROM Transaction WHERE PaymentStatus = 'InProgress' OR PaymentStatus = 'Pending' Having Amount > 3000) as T  GROUP BY VendorID) AS M ")
            myresult = (cur.fetchall())
            return render_template("query3.html", x=myresult);
        elif (queryno == "query4"):
            cur.execute(
                " SELECT V.VendorID,Vendorname,contact,OrderID,CustomerID,Amount,Quantity FROM Vendor V INNER JOIN orders O where V.VendorID = O.VendorID AND Status = 'Active' AND Rating>3 And Quantity > 30   Order by Amount DESC  ")
            myresult = (cur.fetchall())
            return render_template("query4.html", x=myresult);
        elif (queryno == "query5"):
            cur.execute(
                f" SELECT X.VendorID,Vendorname,contact,VAddress FROM AddressVendor AS X INNER JOIN  (SELECT* FROM Vendor WHERE Vendor.VendorID IN (SELECT VendorID FROM ProductInventory WHERE Price > 400 and Quantity > 30) AND Rating < 4) As H WHERE X.VendorID = H.VendorID")
            myresult = (cur.fetchall())
            return render_template("query4.html", x=myresult);
        elif (queryno == "query6"):
            cur.execute(
                f"SELECT CustomerID,Totalitems,Amount,Discount FROM Cart INNER JOIN (SELECT CartID FROM CartContent WHERE Price = (SELECT MAX(Price) FROM CartContent)) AS D WHERE Cart.CartID = D.CartID")
            myresult = (cur.fetchall())
            return render_template("query4.html", x=myresult);
        elif (queryno == "query7"):
            cur.execute(
                f"SELECT * FROM CustomerPaymentMethod C WHERE C.CustomerID IN (SELECT CustomerID FROM (SELECT CustomerID, RANK() OVER (ORDER BY discount DESC) AS Dis_DEC FROM Cart) AS R WHERE Dis_DEC < 3)")
            myresult = (cur.fetchall())
            return render_template("query7.html", x=myresult);
        elif (queryno == "query8"):
            cur.execute(
                "SELECT * FROM ProductInventory INNER JOIN (SELECT ProductID,Pname FROM ProductList WHERE Type= 'CLOTHING' ) AS N WHERE N.ProductID = ProductInventory.ProductID")
            myresult = (cur.fetchall())
            return render_template("query8.html", x=myresult);
        elif (queryno == "query9"):
            cur.execute(
                "SELECT * FROM Orders INNER JOIN (SELECT DISTINCT(CustomerID) FROM  CustomerPaymentMethod where ModeOfPayment = 'Netbanking') AS J WHERE J.CustomerID = Orders.CustomerID AND Orders.Status = 'Active'")
            myresult = (cur.fetchall())
            return render_template("query9.html", x=myresult);
        elif (queryno == "query10"):
            cur.execute(
                "SELECT OrderID,ProductID,Amount,Quantity, RANK() OVER (ORDER BY Amount DESC) AS Amount_Desc FROM  (SELECT* FROM Orders WHERE OrderID IN ( SELECT distinct(OrderID) FROM Transaction WHere PaymentStatus='Done') AND Status ='Active') as o ")
            myresult = (cur.fetchall())
            return render_template("query10.html", x=myresult);
        elif (queryno == "query11"):
            cur.execute(
                f"Select Department FROM (SELECT Department, DENSE_RANK() OVER(ORDER BY Salary Desc)  AS SalaryOrder FROM (SELECT Employee.EmployeeID,Employee.EName,contact,Salary,Department  FROM Employee right  outer join Works ON(Works.EmployeeID = Employee.EmployeeID)) as n)  c WHERE SalaryOrder<5 ")
            myresult = (cur.fetchall())
            return render_template("query11.html", x=myresult);
        elif (queryno == "query12"):
            cur.execute(
                f"SELECT * FROM Transaction JOIN (SELECT OrderID FROM Orders WHERE VendorID IN (SELECT VendorID FROM Vendor WHERE Rating = 0 )) as N WHERE N.OrderID = Transaction.OrderID ")
            myresult = (cur.fetchall())
            return render_template("query12.html", x=myresult);
        elif (queryno == "query13"):
            cur.execute(
                f"SELECT AddressWareHouse.WarehousesID,WarehouseName,WAddress  FROM AddressWareHouse  JOIN (SELECT Warehouses.WarehousesID,WarehouseName FROM Warehouses  JOIN (SELECT distinct(WarehousesID) FROM OwnedBy) as D  where D.WarehousesID = Warehouses.WarehousesID) as l  WHERE l.WarehousesID = AddressWareHouse.WarehousesID")
            myresult = (cur.fetchall())
            return render_template("query13.html", x=myresult);
        elif (queryno == "query14"):
            cur.execute(
                "SELECT DISTINCT(ProductInventory.VendorID) FROM ProductInventory JOIN  (SELECT ProductID FROM OfferHistory WHERE OfferStartDate<'2022-07-01' and OfferEndDate>'2022-08-01') as j  where j.ProductID = ProductInventory.ProductID AND ProductInventory.Status = 'Available' ")
            myresult = (cur.fetchall())
            return render_template("query14.html", x=myresult);

        else:
            return redirect(url_for("queries"))
    else:
        return redirect(url_for("queries"))


if __name__ == '__main__':
    app.run(debug=True, port=50003)
