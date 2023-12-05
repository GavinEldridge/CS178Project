from waitress import serve
from flask import Flask
from flask import request
from flask import render_template
import boto3
from boto3.dynamodb.conditions import Key
TABLE_NAME = "ToyOrders"
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table(TABLE_NAME)
app = Flask(__name__)

@app.route('/')
def hello():
    html= '''<h1> Welcome to Tony's Toy Emporium</h1>'''
    html+='Click <a href=/catalogue>here</a> to view descriptions of models<br>'
    html+= 'Click <a href=/typesquery>here</a> to choose which models to view<br>'
    html+= 'Click <a href=/createorder>here</a> to submit an order<br>'
    html+= 'Click <a href=/deleteorder>here</a> to delete an order<br>'
    return html
    
import pymysql
import creds 

def get_conn():
    conn = pymysql.connect(
        host= creds.host,
        user= creds.user, 
        password = creds.password,
        db=creds.db,
        )
    return conn

def execute_query(query, args=()):
    cur = get_conn().cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows
    
def display_html(rows):
    html = ""
    html += """<table><tr><th>Type</th><th>Desc</th><th>htmldesc</th><th>image</th></tr>"""

    for r in rows:
        html += "<tr><td>" + str(r[0]) + "</td><td>" + str(r[1]) + "</td><td>" + str(r[2]) + "</td><td>" + str(r[3]) + "</td></tr>"
    html += "</table></body>"
    html += '<strong>Click <a href=/>here</a> to return to homepage</strong>'
    return html
    
def display_html2(rows):
    html = ""
    html += """<table><tr><th>Name</th><th>Scale</th><th>Vendor</th><th>Desc</th><th>Stock</th><th>Price</th><th>Order Code</th></tr>"""

    for r in rows:
        html += "<tr><td>" + str(r[0]) + "</td><td>" + str(r[1]) + "</td><td>" + str(r[2]) + "</td><td>" + str(r[3]) + "</td><td>" + str(r[4]) + "</td><td>" + str(r[5]) + "</td><td>" + str(r[6]) + "</td></tr>"
    html += "</table></body>"
    html += '<strong>Click <a href=/>here</a> to return to homepage</strong>'
    return html
@app.route('/catalogue')
def catalogue():
    rows = execute_query("""Select*
                From productlines;""")
    return display_html(rows)
    
@app.route('/type/<types>')
def viewtype(types):
    rows = execute_query("""Select productName, productScale, productVendor, productDescription, quantityInStock, buyPrice, productCode
                From products
                Where productLine = %s;""",(str(types)))
    return display_html2(rows)
    
@app.route("/typesquery", methods = ['GET'])
def types_form():
    return render_template('Radioselect.html')

@app.route("/typesquery", methods = ['POST'])
def types_form_post():
    text = request.form['text']
    return viewtype(text)
    
@app.route("/createorder")
def createorderform():
    return render_template('accountorder.html')
    
@app.route("/createorder", methods=['POST'])
def createorder():
    ordername = request.form['ordername']
    pwd = request.form['pwd']
    ordercode = request.form['order']
    quantity = request.form['quantity']
    table.put_item(
        Item ={
            'ordername': ordername,
            'pwd': pwd,
            'ordercode':ordercode,
            'quantity': quantity,
        }
        )
    html = '''<h1> Your order has been recieved</h1>'''
    html += '<strong>Click <a href=/>here</a> to return to homepage</strong>'
    return html

@app.route("/deleteorder")
def deleteorderform():
    return render_template('deleteorder.html')
    
@app.route("/deleteorder", methods=['POST'])
def deleteorder():
    ordername = request.form['ordername']
    pwd = request.form['pwd']
    html1 = '''<h1> Your order has been deleted</h1>'''
    html1 += '<strong>Click <a href=/>here</a> to return to homepage</strong>'
    html2 = '''<h1> Order not found</h1>'''
    html2 += '<strong>Click <a href=/>here</a> to return to homepage</strong>'
    try:
        table.delete_item(
            Key={
                'ordername': ordername,
                #'pwd': pwd,
            })
        return(html1)
    except:
        return(html2)
    



if __name__=='__main__':
    serve(host='0.0.0.0', port=8080)
    