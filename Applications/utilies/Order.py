from DB.db import mysql_connection, Error

class OrderClass:
    def __init__(self, username, sellerusername, product_Name):
        self.username = username
        self.sellerusername = sellerusername
        self.product_Name = product_Name

        # placeholders for DB values
        self.product_Price = None
        self.product_Quantity = None
        self.sellerlocation = None
        self.buyerlocation = None

        # fetch seller info on init
        self._getSellerInfo()
    
    # ---------------- GET SELLER INFO ----------------
    def _getSellerInfo(self):
        conn = mysql_connection()
        if conn is None:
            return {"status": 500, "message": "DB Connection failed."}

        cursor = conn.cursor(dictionary=True)
        try:
            # Get buyer location
            cursor.execute('SELECT location FROM users WHERE username = %s', (self.username,))
            location = cursor.fetchone()
            if location is None:
                return {"status": 404, "message": "Buyer not found"}
            
            self.buyerlocation = location["location"]

            # Get seller + product info
            query = '''
                SELECT 
                    u.name, u.username, u.location,
                    u.product_Id AS user_product_id,
                    p.product_Id AS product_product_id,
                    p.product_Name, p.product_Price, p.product_Quantity
                FROM users u
                JOIN product p ON u.product_Id = p.product_Id
                WHERE u.username = %s AND p.product_Name = %s
            '''
            cursor.execute(query, (self.sellerusername, self.product_Name))
            datas = cursor.fetchone()
            if datas is None:
                return {"status": 404, "message": "Seller/product not found"}

            self.product_Price = datas["product_Price"]
            self.product_Quantity = datas["product_Quantity"]
            self.sellerlocation = datas["location"]

            return {"status": 200, "sellerInfo": datas, "location": location}

        except Exception as e:
            return {"status": 500, "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    # ---------------- PLACE ORDER ----------------
    def _placeOrder(self, order_quantity, from_location):
        # Check quantity
        if order_quantity > self.product_Quantity:
            return {"status": 400, "message": "Not enough stock"}

        conn = mysql_connection()
        if conn is None:
            return {"status": 500, "message": "DB Connection failed."}

        cursor = conn.cursor(dictionary=True)
        try:
            result_token = self._getUserToken(self.username)
            if result_token["status"] != 200:
                return {"status": result_token["status"], "message": "Buyer token not found"}
            user_Token = result_token["user_Token"]

            result_id = self._getProductId(self.sellerusername)
            if result_id["status"] != 200:
                return {"status": result_id["status"], "message": "Product ID not found"}
            product_Id = result_id["product_Id"]

            # Insert into orders
            order_query = '''
                INSERT INTO orders
                (user_Token, product_Name, product_Price, product_Qty, status, seller, product_Id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(order_query, (
                user_Token,
                self.product_Name,
                self.product_Price,
                order_quantity,
                "Pending",
                self.sellerusername,
                product_Id
            ))
            conn.commit()

            # Fetch the inserted order
            cursor.execute('''
                SELECT * FROM orders
                WHERE user_Token=%s AND seller=%s AND product_Id=%s
                ORDER BY order_Id DESC LIMIT 1
            ''', (user_Token, self.sellerusername, product_Id))
            order = cursor.fetchone()
            if order is None:
                return {"status": 500, "message": "Order insert failed"}

            # Track order movement
            movement_result = self._orderMovement(order["order_Id"], self.buyerlocation, from_location)
            if not movement_result["status"]:
                return {"status": 500, "message": "Failed to track order movement"}

            return {"status": 200, "message": "Product ordered successfully", "order": order}

        except Error:
            conn.rollback()
            return {"status": 500, "message": "Data rollback due to error"}
        finally:
            cursor.close()
            conn.close()

    # ---------------- GET USER TOKEN ----------------
    def _getUserToken(self, username):
        conn = mysql_connection()
        if conn is None:
            return {"status": 500, "message": "DB Connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT user_Token FROM users WHERE username=%s', (username,))
            row = cursor.fetchone()
            if row:
                return {"status": 200, "user_Token": row["user_Token"]}
            return {"status": 404, "message": "User not found"}
        finally:
            cursor.close()
            conn.close()

    # ---------------- GET PRODUCT ID ----------------
    def _getProductId(self, sellerusername):
        conn = mysql_connection()
        if conn is None:
            return {"status": 500, "message": "DB Connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT product_Id FROM users WHERE username=%s', (sellerusername,))
            row = cursor.fetchone()
            if row:
                return {"status": 200, "product_Id": row["product_Id"]}
            return {"status": 404, "message": "Product ID not found"}
        finally:
            cursor.close()
            conn.close()

    # ---------------- UPDATE PRODUCT QUANTITY ----------------
    def _updateProductQuantity(self, quantity, product_Name, sellerusername):
        conn = mysql_connection()
        if conn is None:
            return {"status": False, "message": "DB Connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT product_Id FROM users WHERE username=%s', (sellerusername,))
            row = cursor.fetchone()
            if not row:
                return {"status": 404, "message": "Seller product not found"}

            product_Id = row["product_Id"]
            cursor.execute('UPDATE product SET product_Quantity=%s WHERE product_Id=%s AND product_Name=%s', (quantity, product_Id, product_Name))
            conn.commit()
            return {"status": 200}
        except:
            return {"status": 500, "message": "Failed to update quantity"}
        finally:
            cursor.close()
            conn.close()

    # ---------------- ORDER MOVEMENT ----------------
    def _orderMovement(self, orderId, buyerlocation, sellerlocation):
        conn = mysql_connection()
        if conn is None:
            return {"status": False, "message": "DB Connection failed"}

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('INSERT INTO productMovements(order_Id, from_Location, to_Location) VALUES(%s,%s,%s)', (orderId, buyerlocation, sellerlocation))
            conn.commit()
            return {"status": True}
        except:
            conn.rollback()
            return {"status": False, "message": "Failed to insert order movement"}
        finally:
            cursor.close()
            conn.close()

    def _my_product_quantity(self, token, productname, productquantity):
        conn = mysql_connection()
        if conn is None:
            return {"status": False, "message": "DB Connection failed"}

        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                '''
                SELECT p.product_Id, p.product_Quantity 
                FROM users u 
                JOIN product p ON u.product_Id = p.product_Id 
                WHERE u.user_Token = %s AND p.product_Name = %s
                ''',
                (token, productname)
            )
            productData = cursor.fetchone()

            if productData:
                product_Id = productData["product_Id"]
                product_Quantity = productData["product_Quantity"]

                new_quantity = int(productquantity) + int(product_Quantity)

                cursor.execute(
                    'UPDATE product SET product_Quantity = %s WHERE product_Id = %s AND product_Name = %s',
                    (new_quantity, product_Id, productname)
                )
                conn.commit()
                return {"status": 200}

            else:
                cursor.execute('SELECT product_Id FROM users WHERE user_Token = %s', (token,))
                userData = cursor.fetchone()

                if not userData:
                    return {"status": 404, "message": "User not found"}

                product_Id = userData["product_Id"]
                price = float(0)

                cursor.execute(
                    'INSERT INTO product (product_Name, product_Id, product_Price, product_Quantity) VALUES (%s, %s, %s, %s)',
                    (productname, product_Id, price, int(productquantity))
                )
                conn.commit()

                return {"status": 200}

        except Exception as e:
            conn.rollback()
            return {"status": 500, "message": f"Failed to update your product quantity: {str(e)}"}

        finally:
            cursor.close()
            conn.close()