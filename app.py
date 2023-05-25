
import random
import sys
import uuid

import mariadb
# import pymysql
from flask import (Blueprint, Flask, Response, json, jsonify, redirect,
                   render_template, request)

app = Flask(__name__)

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


@app.route('/', methods=['GET'])
def index():
    result = {'status': 'invalid'}

    return jsonify(result)


@app.route('/request', methods=['GET'])
def requests():

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM requests")
    requests = cursor.fetchall()
    cursor.close()

    total = len(requests)

    return render_template('home.html', requests=requests)

# ------------------------------Pagination-----------------------------


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

# SIR CREATED THIS METHOD


# -------------------------------------Api  test -----------------------------------------
@app.route("/api/t-mate/RegisterDevice", methods=['GET', 'POST'])
def teamate_register_device():

    encrypted_device_id = ""

    result = {
        "status": "error"
    }

    # token = request.headers.get('token')

    if request.method == 'POST':
        if request.is_json:
            content = request.get_json()
            device_id = content['device_id']
            request_id = content['request_id']

            cursor = conn.cursor()
            query = "SELECT * FROM requests WHERE request_id=%s AND device_id=%s"
            value = (request_id, device_id)
            cursor.execute(query, value)
            result = cursor.fetchone()
            cursor.close()

            # validity
            if device_id == "" or device_id == "None" or device_id is None:
                return jsonify({
                    "status": "invalid_request"
                })

            # new registration request

            if (request_id == "" or request_id == "None" or request_id is None):

                content = request.get_json()
                device_id = content['device_id']
                request_id = content['request_id']

                cursor = conn.cursor()
                query = "SELECT * FROM requests WHERE device_id=%s"
                value = (device_id,)
                cursor.execute(query, value)
                result = cursor.fetchone()
                cursor.close()
                if (result):
                    return jsonify({
                        'status': 'Device Exist'
                    })
                else:
                    garden_id = content['garden_id']
                    company = content['organization']
                    requester_name = content['requester_name']
                    requester_contact = content['requester_contact']
                    request_id = (random.randint(1000, 9999))
                    cursor = conn.cursor()
                    query = "INSERT INTO requests (request_id,device_id,company,garden_id,requester_name,requester_contact,status) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                    value = (request_id, device_id, company, garden_id,
                             requester_name, requester_contact, 1)
                    cursor.execute(query, value)
                    conn.commit()
                    cursor.close()
                    result = {
                        "request_id": request_id,
                        "status": "requested"
                    }
                    return jsonify(result)

            # second time  request

            if (result[7] == 1):

                register_token = (str(uuid.uuid4())[0:8])
                cursor = conn.cursor()
                query = "UPDATE requests SET status=%s,register_token=%s WHERE request_id=%s "
                values = (2, register_token, request_id)
                print(request_id)
                cursor.execute(query, values)
                conn.commit()
                cursor.close()

                result = {
                    "request_id": request_id,
                    "reg_token": register_token,
                    "status": "approved"
                }
                return jsonify(result)

        return jsonify({
            'status': 'bad request'

        })

        # print("request_id not found. generating new request")

        # print("device_id not found. generating new request")
        # if found, then provide existing reg-info
        # if not, then generate the request_id

        # else:  # got request id
    return jsonify(result)


@app.route('/get_data', methods=['GET'])
def get_data():
    cursor = conn.cursor()
    query = "SELECT * FROM requests"
    return
# ----------------------AJAX EDIT AND UPDATE-----------------------------------------------


@app.route('/ajaxeditandupdate', methods=['POST'])
def ajaxeditandupdate():
    # data = request.get_json()
    # print(data)
    # request_id = data['request_id']
    request_id = request.form['request_id']
    garden_id = request.form['garden_id']
    requester_name = request.form['requester_name']
    requester_contact = request.form['requester_contact']

    cursor = conn.cursor()
    query = 'UPDATE requests SET garden_id=%s,requester_name=%s,requester_contact=%s WHERE request_id=%s'
    values = (garden_id, requester_name, requester_contact, request_id)
    cursor.execute(query, values)
    conn.commit()
    cursor.close()

    result = {'messege': 'Successful',
              'request_id': request_id, 'garden_id': garden_id,
              'requester_name': requester_name, 'requester_contact': requester_contact}
    return jsonify(result)


# ------------------Ajax Add manual------------------------------------------------------


@app.route('/addmanualdata', methods=['POST'])
def addmanualdata():

    result = {'messege': 'bad request'}

    if (request.method == 'POST'):
        device_id = request.form['device_id']
        company = request.form['company']
        garden_id = request.form['garden_id']
        requester_name = request.form['requester_name']
        requester_contact = request.form['requester_contact']
        cursor = conn.cursor()
        query = 'SELECT * FROM requests WHERE device_id=%s'
        value = (device_id,)
        cursor.execute(query, value)
        result = cursor.fetchone()
        cursor.close()
        if (result):
            return jsonify({'messege': 'This device Already EXIST'})
        else:
            request_id = (random.randint(10000, 10000000))
            cursor = conn.cursor()
            query = "INSERT INTO requests (request_id,device_id,company,garden_id,requester_name,requester_contact,status) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            value = (request_id, device_id, company, garden_id,
                     requester_name, requester_contact, 1)
            cursor.execute(query, value)
            conn.commit()
            cursor.close()
            return jsonify({'messege': 'Requested', 'request_id': request_id})

    return jsonify(result)

# ------------------------------------------------------------------------------------------------------

# -------------------Ajac Code for delete request-------------------------------------------------------


@app.route('/deletepost', methods=['DELETE'])
def deletepost():
    result = {'messege': 'bad request'}
    if (request.method == 'DELETE'):
        request_id = request.form['request_id']
        cursor = conn.cursor()
        query = "DELETE FROM requests WHERE request_id=%s"
        values = (request_id,)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()

        result = {'messege': 'Delete Successfully plese reload  the  page'}
        return jsonify(result)
    return jsonify(result)


# -----------------------------------------------------------------------------------------
    # create app instance
if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=8080,
            debug=True,
            threaded=True,
            use_reloader=True)
