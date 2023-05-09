
import random
import sys
import uuid

import mariadb
# from flask_paginate import Pagination, args, get_page
# import pymysql
from flask import (Blueprint, Flask, json, jsonify, redirect, render_template,
                   request)
from flask_paginate import Pagination, get_page_parameter

app = Flask(__name__)
users = list(range(200))

# Connect to MariaDB


# Instantiate Connection


conn = mariadb.connect(
    host='127.0.0.1',
    port=3300,
    user='rajib',
    password='rajib',
    database='tmate'
)


table_schema_sql_query = '''
    CREATE TABLE IF NOT EXISTS requests (
        id INT(11) NOT NULL AUTO_INCREMENT,
        request_id INT(10) NOT NULL,
        device_id VARCHAR(100) NOT NULL,
        company VARCHAR(100) NOT NULL,
        garden_id VARCHAR(20) NOT NULL,
        requester_name VARCHAR(30) NOT NULL,
        requester_contact VARCHAR(20) NOT NULL,
        status INT(20) NULL,   
        register_token VARCHAR(255)  NULL,
        PRIMARY KEY (id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
'''

# Create the table if it does not exist
cursor = conn.cursor()
cursor.execute(table_schema_sql_query)
conn.commit()
cursor.close()


# Show all the request


@app.route('/request', methods=['GET'])
def requests():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM requests")
    requests = cursor.fetchall()
    cursor.close()
    return render_template('home.html', requests=requests)

# ------------------------------Pagination-----------------------------


def get_users(offset=0, per_page=10):
    return users[offset: offset+per_page]


# Add Requests--------------------------------------------------------


@app.route('/addrequests', methods=['GET', 'POST'])
def addrequest():
    return render_template('addrequest.html')


@app.route('/insert/request', methods=['POST'])
def insertrequest():

    device_id = request.form['device_id']
    cursor = conn.cursor()
    query = 'SELECT * FROM requests WHERE device_id=%s'
    value = (device_id,)
    cursor.execute(query, value)
    result = cursor.fetchone()
    cursor.close()
    # return jsonify({'messege': result[7]})

    if (result):
        if (result[7] == 1):
            return jsonify({'message': 'Already Request'})
        if (result[7] == 4):
            return jsonify({'messege': 'Bloked'})

    else:
        device_id = request.form['device_id']
        company = request.form['company']
        garden_id = request.form['garden_id']
        requester_name = request.form['requester_name']
        requester_contact = request.form['requester_contact']

    #  generate request id
        request_id = (random.randint(10000, 10000000))

        cursor = conn.cursor()
        query = "INSERT INTO requests (request_id,device_id,company,garden_id,requester_name,requester_contact,status) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        value = (request_id, device_id, company, garden_id,
                 requester_name, requester_contact, 1)
        cursor.execute(query, value)
        conn.commit()
        cursor.close()
        return jsonify({'messege': 'Requested', 'request_id': request_id})


# Edit and update request------------------------------------


@app.route('/edit_request/<int:id>/<int:status>')
def edit(id, status):
    if (status == 2):
        register_token = (str(uuid.uuid4())[0:8])
        cursor = conn.cursor()
        query = "UPDATE requests SET status=%s,register_token=%s WHERE id=%s "
        values = (status, register_token, id)
        cursor.execute(query, values)
        cursor.commit()
        cursor.close()
        return jsonify({'message': 'Request APPROVED successfully!',
                        'register_token': register_token})

    if (status == 4):
        cursor = conn.cursor()
        query = "UPDATE requests SET status=%s,register_token=%s WHERE id=%s "
        values = (status, ' ', id)
        cursor.execute(query, values)
        cursor.commit()
        cursor.close()
        return jsonify({'message': 'Request BLOCKED'})
# -----------------------------------------------------------------------------------------
# Ajax-Code--------Update Status-----------------------------------------------------------


@app.route('/updatestatus/<int:status>/<int:request_id>', methods=['PUT'])
def updatestatus(status, request_id):

    # cursor = conn.cursor()
    # query = "UPDATE requests SET status=%s WHERE request_id=%s"
    # value = (status, request_id)
    # cursor.execute(query, value)
    # conn.commit()
    # cursor.close()
    # return jsonify({'message': 'success'})
    #  request_id = request.form['request_id']
    # status = request.form['status']
    if (status == 2):

        register_token = (str(uuid.uuid4())[0:8])
        cursor = conn.cursor()
        query = "UPDATE requests SET status=%s,register_token=%s WHERE request_id=%s "
        values = (status, register_token, request_id)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        return jsonify({'message': 'Request APPROVED successfully!',

                        })
        # 'register_token': register_token})
        # return jsonify({'message': status})

    elif (status == 4):
        cursor = conn.cursor()
        query = "UPDATE requests SET status=%s,register_token=%s WHERE request_id=%s "
        values = (status, ' ', request_id)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        return jsonify({'message': 'Request BLOCKED'})

    else:

        cursor = conn.cursor()
        query = "UPDATE requests SET status=%s,register_token=%s WHERE request_id=%s "
        values = (status, ' ', request_id)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        return jsonify({'message': 'Requested'})
        # return jsonify({'message': status})

 # ---------------------AJAX FECTH DATA----------------------------------------------------


@app.route('/get_data', methods=['GET'])
def get_data():
    cursor = conn.cursor()
    query = "SELECT * FROM requests"
    return


# -----------------------------------------------------------------------------------------
    # create app instance
if __name__ == '__main__':
    app.run(host='127.0.0.1',
            port=8080,
            debug=True,
            threaded=True,
            use_reloader=True)
