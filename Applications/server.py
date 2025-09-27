from flask import Flask, render_template, redirect, request, url_for, jsonify, session

#----- DATABASE CONNECTION ----
from DB.db import mysql_connection, Error

# OPEARTION
from utilies.AuthendicationCheck import AuthendicationCHK
from utilies.Product import ProductClass, ProductCreateClass
from utilies.Order import OrderClass

server = Flask(__name__)
server.secret_key = '1234567890'

mysql = mysql_connection()

@server.route("/", methods=['GET'])
def root():
    conn = mysql_connection()
    if conn is None:
        return render_template("Index.html", message='DB Connection failed.'), 500

    cursor = conn.cursor(dictionary=True)
    
    if "user" not in session:
        return redirect(url_for('login'))
    
    current_user = session.get("user")
    username = current_user.get("username")


    try:
        query = '''
            SELECT 
                u.name,
                u.username,
                u.product_Id AS user_product_Id,
                p.product_Id AS product_product_Id,
                p.product_Name, 
                p.product_Price, 
                p.product_Quantity
            FROM users u
            JOIN product p
            ON u.product_Id = p.product_Id
            WHERE u.username != %s
        '''
        cursor.execute(query, (username,))
        productDatas = cursor.fetchall()

        return render_template('Index.html', informations=productDatas), 200

    except Exception as e:
        return render_template('Index.html', message='Internal Server Error'), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@server.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools():
    return {}, 204

#----- AUTHENDICATION'S ----

#--- LOGIN COMPONENT ---
@server.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('Auth/Login.html'), 200

    elif request.method == 'POST':
        data = request.get_json(silent=True) or request.form

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                "status": 400,
                "message": "All fields are required. CODE=400"
            }), 400

        try:
            method = AuthendicationCHK(username, password)

            check_username = method._userChk()

            if not check_username:
                return jsonify({
                    "status": 404,
                    "message": "Username not found."
                }), 404

            check_password = method._passChk()

            if not check_password:
                return jsonify({
                    "status": 401,
                    "message": "Wrong password."
                }), 401

            session['user'] = { 'username':username }

            return jsonify({ "status": 200, "message": "User Login Successfully." }), 200

        except Exception as err:
            return jsonify({
                "status": 500,
                "message": "Internal Server Error. CODE=500"
            }), 500

#--- CREATE ACCOUNT COMPONENT ----
@server.route("/create", methods=['POST', 'GET'])
def register():

    if request.method == 'GET':
        return render_template('Auth/Create.html'), 200
    
    elif request.method == 'POST':
        data = request.get_json(silent=True) or request.form

        name = data.get('name')
        username = data.get('username')
        password = data.get('password')
        location = data.get('location')

        if not name or not username or not password or not location:
            return jsonify({"status": 400, "message": "All field Required."}), 400

        conn = mysql_connection()
        if conn is None:
            return jsonify({
                "status": 500,
                "message": "DB Connection failed."
            }), 500
            
        cursor = None
        
        try:
            method = AuthendicationCHK(username, password)

            if method._userChk():
                return jsonify({
                    "status": 409,
                    "message": "Username already Existed."
                }), 409

            cursor = conn.cursor(dictionary=True)
            query = '''
                INSERT INTO users (name, username, password, location) 
                VALUES (%s, %s, %s, %s);
            '''
            value = (name, username, password, location)
            cursor.execute(query, value)
            conn.commit()

            return jsonify({"status": 201, "message": "User Created."}), 201

        except Error as e:
            conn.rollback()
            return jsonify({"status": 500, "message": str(e)}), 500

        finally:
            if cursor: cursor.close()
            if conn: conn.close()

#--- PROFILE COMPONENT ---
@server.route('/profile')
def profile():
	if "user" not in session:
		return jsonify({ "status":404, "message":"User Not found."}), 404
	
	current_user = session.get("user")
	username = current_user.get("username")

	conn = mysql_connection()
	if conn is None:
		return jsonify({ "status":500, "message":"DB Connection failed."}), 500
	
	cursor = None

	try:

		cursor = conn.cursor(dictionary=True)
		query = 'SELECT name, username, location, product_Id FROM users WHERE username = %s'
		value = (username, )

		cursor.execute(query, value)
		user_details = cursor.fetchone()

		if not user_details:
			return jsonify({ "status":404, "message":"User details not found"}), 404
		
		return jsonify({
			"status":200,
			"message":"User detail fetched successfully",
			"user":user_details
		}), 200

	except Exception as e:

		return jsonify({ "status":500, "message":f"Internal server Error {str(e)}"}), 500
	
	finally:

		cursor.close()
		conn.close()

#--- LOGOUT COMPONENT ---
@server.route('/logout')
def logout():
	session.pop("user", None)
	return redirect(url_for('root'))

#----- PRODUCT'S -----

@server.route("/product", methods=['GET'])
def product():
    if "user" not in session:
        return redirect(url_for('root')), 404

    conn = mysql_connection()
    if conn is None:
        return render_template("Index.html", message="DB Connection failed."), 500

    cursor = conn.cursor(dictionary=True)

    userLogin = session.get("user") or {}
    username = userLogin.get("username")
    if not username:
        return render_template("Index.html", message="Invalid session user."), 400

    try:
        query = '''
            SELECT 
                u.username, 
                u.product_Id AS user_product_id, 
                p.product_Id AS product_product_id, 
                p.product_Name, 
                p.product_Price, 
                p.product_Quantity
            FROM users u
            JOIN product p
              ON u.product_Id = p.product_Id
            WHERE u.username = %s
        '''
        cursor.execute(query, (username,))
        productDatas = cursor.fetchall()

        if not productDatas:
            return render_template("Index.html", message="No products found."), 404

        return render_template('Index.html', products=productDatas), 200

    except Exception as e:
        return render_template('Index.html', message="Internal server error."), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@server.route("/product", methods=['POST'])
def addProduct():
    data = request.get_json(silent=True) or request.form

    productname = data.get('productname')
    productprice = data.get('productprice')
    productquantity = data.get('productquantity')

    if not productname or not productprice or not productquantity:
        return jsonify({ "status": 400, "message": "All fields required." }), 400

    if "user" not in session:
        return jsonify({ "status": 500, "message": "User not found." }), 500

    current_user = session.get("user")
    username = current_user.get("username")

    try:
        method = ProductClass(username, productname)
        result = method._chkProduct()

        if result["status"] == 200:
            return jsonify({
                "status": 400,
                "message": "Product already in stock, change the product name."
            }), 400

        productprice = float(productprice)
        productquantity = int(productquantity)

        createMethod = ProductCreateClass(username, productname, productprice, productquantity)
        success, message = createMethod._create()

        if success:
            return jsonify({ "status": 201, "message": message }), 201
        else:
            return jsonify({ "status": 500, "message": message }), 500

    except Exception as e:
        return jsonify({ "status": 500, "message": str(e) }), 500

@server.route("/product/<string:productname>", methods=['GET','POST'])
def editProduct(productname):
    conn = mysql_connection()
    if conn is None:
        return jsonify({"status": 500, "message": "DB Connection failed."}), 500
    cursor = conn.cursor(dictionary=True)

    if "user" not in session:
        return jsonify({"status": 500, "message": "User not found."}), 500

    users = session.get("user")
    username = users.get("username")

    if request.method == "GET":
        try:
            cursor.execute("SELECT product_Id FROM users WHERE username=%s", (username,))
            userData = cursor.fetchone()
            product_Id = userData["product_Id"]

            cursor.execute("""
                SELECT product_Name, product_Price, product_Quantity 
                FROM product 
                WHERE product_Id=%s AND product_Name=%s
            """, (product_Id, productname))
            productData = cursor.fetchone()

            if not productData:
                return jsonify({"status":404, "message":"Product not found."}), 404

            return render_template("Product/ProductUpdate.html", product=productData)

        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    elif request.method == "POST":
        try:
            new_price = request.form.get("product-price")
            new_quantity = request.form.get("product-quantity")

            cursor.execute("SELECT product_Id FROM users WHERE username=%s", (username,))
            userData = cursor.fetchone()
            product_Id = userData["product_Id"]

            cursor.execute("""
                UPDATE product
                SET product_Price=%s, product_Quantity=%s
                WHERE product_Id=%s AND product_Name=%s
            """, (new_price, new_quantity, product_Id, productname))
            conn.commit()

            return redirect(url_for("product"))

        finally:
            if cursor: cursor.close()
            if conn: conn.close()

#---- END PRODCUT ----

#---- ORDER ----
@server.route("/order", methods=['GET'])
def order():
    conn = mysql_connection()
    if conn is None:
        return render_template("Index.html", message='DB Connection failed.'), 500

    cursor = conn.cursor(dictionary=True)
    
    if "user" not in session:
        return redirect(url_for('login'))
    
    current_user = session.get("user")
    username = current_user.get("username")

    try:
        cursor.execute('SELECT user_Token FROM users WHERE username = %s', (username,))
        users = cursor.fetchone()
        user_Token = users["user_Token"]

        cursor.execute('SELECT * FROM orders o JOIN productMovements p ON o.order_Id = p.order_Id WHERE o.user_Token =%s', (user_Token,))
        ordersInfo = cursor.fetchall()

        cursor.execute('SELECT * FROM orders o JOIN productMovements p JOIN users u ON o.order_Id = p.order_Id AND o.user_Token = u.user_Token WHERE o.seller = %s AND o.status = %s', (username, 'pending',))
        orderRequest = cursor.fetchall()

        return render_template('Index.html', orders=ordersInfo, requests=orderRequest)
    except Exception as e:
        return render_template("Index.html", message=str(e)), 200
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@server.route("/order/<string:username>/<string:product_Name>", methods=['GET', 'POST'])
def neworder(username, product_Name):
    if "user" not in session:
        return jsonify({"status": 500, "message": "User not found."}), 500

    current_user = session.get("user")
    my_user_name = current_user.get("username")

    methodClass = OrderClass(my_user_name, username, product_Name)

    if request.method == 'GET':

        result = methodClass._getSellerInfo()

        if result["status"] == 404:
            return render_template('Orders/NewOrder.html', message=result["message"]), 404
        
        return render_template( 'Orders/NewOrder.html', warehouse=result["sellerInfo"], to_location=result["location"] ), 200

    elif request.method == 'POST':
        quantity = request.form.get("productquantity")
        seller_location = request.form.get("sellerlocation")

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return render_template("Orders/NewOrder.html", message="Invalid quantity"), 400

        result = methodClass._placeOrder(quantity, seller_location)

        if result["status"] != 200:
            return render_template("Orders/NewOrder.html", message=result.get("message", "Order failed")), 500
        
        return redirect(url_for('root'))

@server.route("/order/<string:movementId>", methods=['GET','POST'])
def editTrack(movementId):
    conn = mysql_connection()
    if conn is None:
        return jsonify({"status": 500, "message": "DB Connection failed."}), 500
    cursor = conn.cursor(dictionary=True)

    if "user" not in session:
        return render_template("Index.html", message="User not found.")

    if request.method == 'GET':

        try:
            cursor.execute('SELECT * FROM productMovements WHERE movement_Id = %s', (movementId,))
            movement = cursor.fetchone()

            return render_template("Orders/UpdateTrack.html", movements=movement), 200
        except Exception as e:
            return render_template("Orders/UpdateTrack.html", message="Internal server error"), 200
        finally:
            cursor.close()
            conn.close()

    elif request.method == 'POST':
        try:
            tolocation = request.form.get('buyerlocation')
            cursor.execute('UPDATE productMovements SET to_Location = %s WHERE movement_Id = %s', (tolocation, movementId, ))
            conn.commit()

            return redirect(url_for('order'))
        except Exception as e:
            conn.rollback()
            return render_template("Index.html", message="Data rollback()"), 500
        finally:
            cursor.close()
            conn.close()

@server.route("/order/accept", methods=['POST'])
def accept():
    conn = mysql_connection()
    if conn is None:
        return jsonify({"status": 500, "message": "DB Connection failed."}), 500
    cursor = conn.cursor(dictionary=True)

    if "user" not in session:
        return jsonify({"status": 500, "message": "User not found."}), 500

    users = session.get("user")
    username = users.get("username")

    if request.method == 'POST':
    
        orderId = request.form.get('orderId')
        status = 'delivery'
        qty = request.form.get('productQty')

        try:
            cursor.execute('SELECT p.product_Quantity FROM orders o JOIN product p ON o.product_Id = p.product_Id AND o.product_Name = p.product_Name WHERE o.order_Id = %s', (orderId,))
            productQty = cursor.fetchone()

            if int(productQty["product_Quantity"]) < int(qty):
                return render_template("Index.html", message="Not accept the Request. Becuase product quantity is low.")

            cursor.execute(
                'UPDATE orders SET status = %s WHERE order_Id = %s',
                (status, orderId)
            )
            conn.commit()
    
            cursor.execute(
                'SELECT * FROM orders WHERE order_Id = %s',
                (orderId,)
            )
            fetchData = cursor.fetchone()

            user_Token = fetchData["user_Token"]
            product_Name = fetchData["product_Name"]
            sellerusername = fetchData["seller"]
            product_Quantity = fetchData["product_Qty"]
    
            methodClass = OrderClass(username, sellerusername, product_Name)
    
            cursor.execute(
                'SELECT product_Quantity FROM product WHERE product_Id = %s AND product_Name = %s',
                (fetchData["product_Id"], fetchData["product_Name"])
            )
            product_Qty = cursor.fetchone()

            quantity = float(product_Qty["product_Quantity"]) - float(product_Quantity)
            quantityUpdate = methodClass._updateProductQuantity(quantity, product_Name, sellerusername)
            if quantityUpdate["status"] != 200:
                return render_template("Index.html", message="Product quantity updation error.")

            balanceUpdate = methodClass._my_product_quantity(user_Token, product_Name, product_Quantity)
            if balanceUpdate["status"] != 200:
                return render_template("Index.html", message="my product quantity updation error.")


            cursor.execute(
                'UPDATE productMovements SET delivery_time = NOW() WHERE order_Id = %s',
                (orderId,)
            )
            conn.commit()

    
            return redirect(url_for('order', message=f"Order Accepted."))
    
        except Error as e:
            conn.rollback()
            return render_template("Index.html", message="Internal Server Error."), 500
    
        finally:
            cursor.close()
            conn.close()
    
@server.route("/order/cancel", methods=['POST'])
def cancel():
    conn = mysql_connection()
    if conn is None:
        return jsonify({"status": 500, "message": "DB Connection failed."}), 500
    cursor = conn.cursor(dictionary=True)

    if "user" not in session:
        return jsonify({"status": 500, "message": "User not found."}), 500

    if request.method == 'POST':

        orderId = request.form.get('orderId')
        status = 'canceled'

        try:
            print('Test 1')
            cursor.execute('UPDATE orders SET status = %s WHERE order_Id = %s', (status, orderId))
            conn.commit()

            print('Test 2')

            return redirect(url_for("order", message=f"Order cancelled."))
        except Exception as e:
            return render_template("Index.html", message="Internal Server Error"), 500
        
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for("root"))

#---- END ORDER ----

#---- REPORT ----
@server.route("/report", methods=['GET'])
def report(): 
    if "user" not in session:
        return render_template("Index.html", message='User not found.'), 500
    
    conn = mysql_connection()
    if conn is None:
        return render_template("Index.html", message="DB Connection failed."), 500
    
    cursor = conn.cursor(dictionary=True)
    user = session.get("user")
    username = user.get("username")

    try:

        cursor.execute('SELECT user_Token, product_Id FROM users WHERE username = %s', (username, ))
        users = cursor.fetchone()

        user_Token = users["user_Token"]
        product_Id = users["product_Id"]

        # ORDERS REPORT
        ordersquery = '''
            SELECT 
                o.order_Id,
                o.product_Name,
                o.product_Qty AS IssuedQty,
                p.product_Quantity AS TotalQty,
                (p.product_Quantity - o.product_Qty) AS InitialQty, 
                o.status,
                o.seller,
                o.ordered_By,
                m.from_Location,
                m.to_Location
            FROM orders o
            JOIN productMovements m ON o.order_Id = m.order_Id
            JOIN product p ON o.product_Name = p.product_Name
            WHERE o.user_Token = %s
            AND p.product_Id = %s
            AND o.status IN ('delivery', 'canceled')
        '''

        cursor.execute(ordersquery, (user_Token, product_Id, ))
        orderdata = cursor.fetchall()
        print(orderdata)
        return render_template("Report/Reports.html", orders=orderdata), 200
    except Exception as e:
        return render_template("Report/Reports.html", message=f"Internal Server Error. {str(e)}"), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
	port = '3000'
	server.run(debug=True, port=port)