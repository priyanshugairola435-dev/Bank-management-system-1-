from flask import Flask, render_template, request,redirect,session
import sqlite3

app = Flask(__name__)


conn = sqlite3.connect("user.db")
app.secret_key="your_secret_key_here"
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT,
    ac_no TEXT PRIMARY KEY,
    password TEXT,
    balance REAL
)
""")
conn.commit()
conn.close()

@app.route('/', methods=['GET','POST'])
def home():
  if request.method == 'POST':
      ac_no=request.form['ac_no']
      password=request.form['password']
      conn = sqlite3.connect("user.db")
      cursor = conn.cursor()
      cursor.execute("select * from users where ac_no=? AND password=?",(ac_no,password))
      user = cursor.fetchone()
      conn.close()
      if ac_no == "112233":
          if password == "1526":
              return redirect("/admin")
      else:
          pass
      if user:
          session['ac_no']=ac_no
          return redirect('/dashboard')
      else:
          return "wrong"
      
  
  return render_template("ac_login.html")

@app.route('/createAC', methods=['GET', 'POST'])
def createAC():
    if request.method == 'POST':
        username = request.form['username']
        ac_no = request.form['ac_no']
        password = request.form['password']

       
        conn = sqlite3.connect("user.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(ac_no, password, username,balance) VALUES (?, ?, ?,10000)",
            (ac_no, password, username)
        )

        conn.commit()
        conn.close()

        return "done"

    return render_template("ac_create.html")

@app.route('/dashboard')
def dash():
    return render_template("index.html")

@app.route('/transfer',methods=['GET','POST'])
def transfer():
    if request.method == 'POST':
        ac_no=request.form['ac_no']
        password=request.form['password']
        receiver=request.form['receiver']
        amount=float(request.form['amount'])
        conn = sqlite3.connect("user.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * from users where ac_no=? and password=?",(ac_no,password))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return "ac no. and password are wrong"
        cursor.execute(" SELECT * FROM users where ac_no=?",(receiver,))
        reci = cursor.fetchone()
        if not reci:
            conn.close()
            return " invalid reciever ac number."
        sender_balance = user[3]
        if amount > sender_balance:
            conn.close()
            return " insufficient balance!"
        new_balance = sender_balance - amount
        cursor.execute("UPDATE users SET balance=? where ac_no =?",(new_balance,ac_no))
        reci_balance=reci[3]
        reci_new_balance=reci_balance+amount
        cursor.execute("UPDATE  users SET balance=? where ac_no=?",(reci_new_balance,receiver))
        conn.commit()
        conn.close()
        return render_template("moneytransdone.html",sender=ac_no,
    receiver=receiver,
    amount=amount,
    new_balance=new_balance)
    return render_template("trans.html")
    
@app.route('/success')
def success():
    return render_template("moneytransdone.html")

@app.route('/balance')
def balance():

    if 'ac_no' not in session:
        return redirect('/') 

    
    ac_no = session['ac_no']

   
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE ac_no=?", (ac_no,))
    user = cursor.fetchone()
    conn.close()

    balance = user[0]
    return render_template("check.html",balance=balance)

@app.route("/admin")
def admin():
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username,password,ac_no,balance from users")
    users= cursor.fetchall()
    conn.close()
    return render_template("admin.html",users=users)

if __name__ == "__main__":
    app.run(debug=True)