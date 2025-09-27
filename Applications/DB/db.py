import mysql.connector
from mysql.connector import Error

db_config = {
	'host':'localhost',
	'username':'root',
	'password':'Suriya@p1102',
	'database':'inventorysoftware',
}

def mysql_connection():
	try:
		conn = mysql.connector.connect(**db_config)
		return conn
	except Error as e:
		print(e)
		return None