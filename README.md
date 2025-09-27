# Inventory Management System

A **small inventory management software** built using **Flask (Python)** and **MySQL** to manage product requests, stock balance, and order history between warehouses.

---

## Features

### Authentication
- `/login` - User login screen.  
- `/register` - User registration screen.  
- Uses **Flask sessions** to manage authenticated users.

### Product Management
- `/product`  
  - Add a new product.  
  - Edit product information.  
  - View all products.

### Order Management
- `/order`  
  - Request products from Warehouse A to Warehouse B.  
  - Accept or decline product requests.  
  - Edit product destination.

### Reports
- `/report`  
  - View balance quantity stock.  
  - View order history with statuses.

### Home
- `/` - Home screen with navigation to all modules.

---

## Technology Stack
- **Backend:** Python, Flask  
- **Database:** MySQL (using `mysql.connector`)  
- **Frontend:** HTML, CSS, JavaScript (with Jinja2 templates)  

---

## Installation

Follow these steps to set up the project locally:

### 1. Clone the repository
```bash
git clone https://github.com/suria003/Inventorymanagementsoftware.git
cd Inventorymanagementsoftware/Applications

## Create virtual environment
python3 -m venv venv

## Activate on Linux/Mac
source venv/bin/activate

## Activate on Windows
venv\Scripts\activate

### 2. Install required packages

pip3 install -r requirements.txt


### Server Start

python3 server.py