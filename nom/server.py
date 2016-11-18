  #!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver
To run locally
    python server.py
Go to http://localhost:8111 in your browser
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for
import time
import sys



tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following uses the postgresql test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/postgres
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# Swap out the URI below with the URI for the database created in part 2
DATABASEURI = "postgresql://yt2456:98c5y@104.196.175.120/postgres"
#104.196.175.120
#104.196.180.73

#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#
#engine.execute("""DROP TABLE IF EXISTS test;""")
#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
#
# END SQLITE SETUP CODE
#



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:
  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print (request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM restaurant")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
  return render_template("anotherfile.html")


@app.route('/allrestaurant')
def allrestaurant():

  #g.conn.execute("Insert into restaurant values (12, 'Thai Market', '11', '22')")

  cursor = g.conn.execute("""select r.name, rc.cuisince, rc.price, a.street, a.city, a.state, a.zip from restaurant r, restaurantcategory rc, address a where (r.restaurantid = 
                             rc.restaurantid and r.restaurantid = a.restaurantid);""")

  names = []
  for result in cursor:
    name = result[0]
    cuisine = result[1]
    address = result[3].strip() + ", " + result[4].strip() + ", " + result[5].strip() + ", " + str(result[6]).strip()
    names.append([name, cuisine, address])  # can also be accessed using result[0]
  cursor.close()


  context = dict(data = names)


  return render_template("allrestaurant.html", **context)


@app.route('/addarestaurant')
def addarestaurant():

  return render_template("addarestaurant.html")

@app.route('/menu/<restaurant>')
def menu(restaurant):
  cursor = g.conn.execute(""" select name, price from items i where 
                              i.restaurantid = (select restaurantid from 
                              restaurant r where r.name = %s);""", restaurant)

  items = []
  # items.append("Item" + ' ' * 20 + "Price")
  for result in cursor:
      items.append([result['name'],result['price']])

  cursor.close()

  context = dict(data = items, rest = restaurant)
  return render_template("menu.html", **context)


@app.route('/addmenu/<restaurant>', methods = ['POST'])
def addmenu(restaurant):
  print("restaurant")
  name = check(request.form['item'])
  price = check(request.form['pr'])

  if name == None or price == None:
    
    context = "/menu/" + restaurant
    return render_template("error.html", url = context)

  id = int(g.conn.execute("select last_value from items_id_seq").first()['last_value'])


  restid = int(g.conn.execute("""select restaurantid from restaurant where name = %s""", restaurant).first()['restaurantid'])
  
  cmd = 'INSERT INTO items values ((:id), (:name1), (:name2), (:name3))'
  g.conn.execute(text(cmd), id = id, name1 = name, name2 = price, name3 = restid)

  seqname = 'items_id_seq'
  inc = 'Select nextval((:name))'
  g.conn.execute(text(inc), name = seqname)
  

  return redirect(url_for('menu', restaurant = restaurant))



@app.route('/addrestaurant', methods = ['POST'])
def addrestaurant():

  rname = check(request.form['nm']) 
  otime = check(request.form['op'])
  ctime = check(request.form['ct'])
  category = check(request.form['cat']) 
  waiting = check(request.form['wt'])
  price = check(request.form['pr'])


  street = check(request.form['str']) 
  city = check(request.form['cty'])
  state = check(request.form['sta'])
  country = check(request.form['cou']) 
  z = check(request.form['zip']) 


  if rname == None or otime == None or ctime == None or category == None or waiting == None or price == None or street == None or city == None or state == None or country == None or z == None:    
    
    context = "/addarestaurant"
    return render_template("error.html", url = context)

  id = int(g.conn.execute("select last_value from rest_id_seq").first()['last_value'])
  
  
  cmd = 'INSERT INTO restaurant values ((:id), (:name1), (:name2), (:name3))'
  g.conn.execute(text(cmd), id = id, name1 = rname, name2 = otime, name3 = ctime)

  try:
    cid = g.conn.execute(" select cid from categorys where cname = %s", category).first()['cid']

    restcat = 'INSERT INTO restaurantcategory values ((:cid), (:cat), (:wait), (:pr), (:id))'
    g.conn.execute(text(restcat), cid = int(cid), cat = category, wait = waiting, pr = price, id = id)
  except TypeError: 
    newcid = int(g.conn.execute("select last_value from cat_id_seq").first()['last_value'])

   

    cat = 'INSERT INTO categorys values ((:cid), (:cname))'

    g.conn.execute(text(cat), cid = newcid, cname = category)

    restcat = 'INSERT INTO restaurantcategory values ((:cid), (:cat), (:wait), (:pr), (:id))'
    g.conn.execute(text(restcat), cid = newcid, cat = category, wait = waiting, pr = price, id = id)

    

    
    seqname = 'cat_id_seq'
    inc = 'Select nextval((:name))'
    g.conn.execute(text(inc), name = seqname)
  

  
  

  add = 'INSERT INTO address values ((:id), (:x1), (:x2), (:x3), (:x4), (:x5), (:x6))'
  g.conn.execute(text(add), id = id, x1 = street, x2 = z, x3 = city, x4 = state, x5 = country, x6 = id)

  seqname = 'rest_id_seq'
  inc = 'Select nextval((:name))'
  g.conn.execute(text(inc), name = seqname)


  return redirect('/allrestaurant')

def check(statement):
  
  if (statement == None or statement == ""):
    return None

  s = statement.lstrip(' ').lower()
  
  if s== None or s[0] == "'" or 'delete' in s or 'insert' in s or s[-1] == '-':
    return None 
  else:
    return statement

@app.route('/checkhistory')
def checkhistory():
  return render_template("checkhistory.html")


@app.route('/userinfo', methods = ['POST'])
def userinfo():
  uname = check(request.form['us'])
  password = check(request.form['ps'])

  if uname == None or password == None:
    context = "/checkhistory"
    return render_template("error.html", url = context)

  print(uname + " " + password)

  try:
    uid = g.conn.execute(" select uid from users where email = %s and password = %s", uname, password).first()['uid']


    cursor = g.conn.execute("""select r.name, u.timespicked from userhistory u, restaurant r
                               where (u.restaurantid = r.restaurantid and u.uid = %s);""", int(uid))
    
    names = []
    for result in cursor:
      print(result)
      names.append([result[0], str(result[1])])

    cursor.close()

    context = dict(data = names)
 
    return render_template("userhistory.html", **context)

  except TypeError:
    context = "/checkhistory"

    return render_template("error.html", url = context)



# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print (name)
  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
  g.conn.execute(text(cmd), name1 = name, name2 = name);

  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


@app.route('/search')
def search():

  cursor = g.conn.execute(""" SELECT DISTINCT cuisince FROM restaurantcategory """)
  info = []
  for result in cursor:
    info.append(result['cuisince'])
  cursor.close()

  
  context = dict(info = info)
  return render_template("search.html", **context)


@app.route('/suggest', methods=['POST'])
def suggest():
  cuisine = check(request.form['cuisine'])
  waittime = check((request.form['time']))
  price = check((request.form['price']))
  hour = check((request.form['hour']))

  print(hour)
  print(time.strftime("%H"))
  print (cuisine)
  print (waittime)
  print (price)

  if cuisine == None or waittime == None or price == None or hour == None:
    context = "/search"
    return render_template("error.html", url = context)

  waittime = int(waittime)
  price = int(price)
  hour = float(hour) / 60

  lowbound = price - 10
  if price == 30:
    price = sys.maxsize
    lowbound = 20
  
  print(lowbound)
  print(price)
  # hour = 15
  hour = hour + float(time.strftime("%H")) + float(time.strftime("%M")) / 60
  
  

  info = []
  cursor = g.conn.execute(""" SELECT name FROM restaurant a WHERE a.restaurantid IN (SELECT restaurantid FROM restaurantcategory b WHERE b.cuisince = %s AND b.waittime <= %s AND b.price >= %s AND b.price < %s) AND a.closing <= %s AND a.opening > %s;""", cuisine, waittime, lowbound, price, hour, hour)
  for result in cursor:
    info.append(result['name'])
  cursor.close()

  context = dict(info = info)

  return render_template("suggest.html", **context)

@app.route('/order/<restaurant>', methods = ['POST'])
def order(restaurant):
  uname = check(request.form['us'])
  password = check(request.form['ps'])
  print (uname)
  print(password)
  if uname == None or password == None:
    context = "/menu/" + restaurant
    return render_template("error.html", url = context)

  try:
    uid = g.conn.execute(" select uid from users where email = %s and password = %s", uname, password).first()['uid']
    rid = g.conn.execute(" select restaurantid from restaurant where name = %s", restaurant).first()['restaurantid']
    print(rid)
    print(uid)

    print("inner try")
    x = g.conn.execute("select * from userhistory where uid = %s and restaurantid = %s", int(uid), int(rid)).first()

    if x != None: 
      g.conn.execute("update userhistory set timespicked = (timespicked + 1) where uid = %s and restaurantid = %s", int(uid), int(rid))
      #cur = g.conn.execute("select * from userhistory where uid = %s and restaurantid = %s", int(uid), int(rid))

    else:
       g.conn.execute("Insert into userhistory values (%s, %s, 1)", int(uid), int(rid))



    cur = g.conn.execute("select r.name, u.timespicked from userhistory u, restaurant r where (u.restaurantid = r.restaurantid and u.uid = %s and u.restaurantid = %s)", int(uid), int(rid))

    names = []
    # names.append['Thank you for order!']


    for result in cur:
      print(result)
      names.append([result[0], str(result[1])])

    cur.close()

    context = dict(data = names)
 
    return render_template("userhistory.html", **context)

  except TypeError:
    print("type error")
    context = "/menu/" + restaurant
    return render_template("error.html", url=context)


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
