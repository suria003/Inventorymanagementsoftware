from DB.db import mysql_connection, Error

class ProductClass:
    def __init__(self, username, productname):
        self.username = username
        self.productname = productname

    def _chkProduct(self):
        conn = mysql_connection()
        if conn is None:
            return { "status": 500, "message": "DB connection failed." }

        cursor = conn.cursor(dictionary=True)
        try:
            query = '''
                SELECT 
                    u.username,
                    u.product_Id AS user_product_id,
                    p.product_Id AS product_product_id,
                    p.product_Name 
                FROM users u
                JOIN product p
                ON u.product_Id = p.product_Id
                WHERE u.username = %s AND p.product_Name = %s
            '''
            value = (self.username, self.productname)
            cursor.execute(query, value)
            result = cursor.fetchone()

            if result:
                return {
                    "status": 200,
                    "message": "Product already exists.",
                }
            else:
                print('pass 404')
                return { "status": 404, "message": "Product not found." }

        except Exception as e:
            return { "status": 500, "message": str(e) }

        finally:
            if cursor: cursor.close()
            if conn: conn.close()

from DB.db import mysql_connection, Error

class ProductCreateClass:
    def __init__(self, username, productname, productprice, productquantity):
        self.username = username
        self.productname = productname
        self.productprice = productprice
        self.productquantity = productquantity

    def _create(self):
        conn = mysql_connection()
        if conn is None:
            return False, "DB Connection failed."

        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute('SELECT product_Id FROM users WHERE username = %s', (self.username,))
            user_data = cursor.fetchone()

            if not user_data:
                return False, f"No user found with username '{self.username}'."

            product_id = user_data["product_Id"]

            query = '''
                INSERT INTO product (product_Name, product_Id, product_Price, product_Quantity)
                VALUES (%s, %s, %s, %s)
            '''
            value = (self.productname, product_id, self.productprice, self.productquantity)

            cursor.execute(query, value)
            conn.commit()

            return True, "Product created successfully."

        except Error as e:
            conn.rollback()
            return False, str(e)

        finally:
            if cursor: cursor.close()
            if conn: conn.close()