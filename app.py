from flask import Flask,redirect,render_template,url_for,request,session
from flask import flash
from flask_mysqldb import MySQL
from flask_mail import Mail,Message
import secrets
import re

app=Flask(__name__)

app.config['MYSQL_HOST']="localhost"
app.config['MYSQL_USER']="root"
app.config['MYSQL_PASSWORD']=""
app.config['MYSQL_DB']="flask_db"

mysql=MySQL(app)


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']='laytonmatheka7@gmail.com'
app.config['MAIL_PASSWORD']='qamfnggyldkpbhje'
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
mail=Mail(app)


app.secret_key="layton"

#landing page
@app.route('/')
def home():
    return render_template("home.html")

# obtaining user inputs
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT username FROM users ")
        result = cur.fetchall()
        existing_usernames = [row[0] for row in result]
        if username in existing_usernames:
            flash("Username is already taken try another one...")
            return render_template('register.html', name=name, username=username, email=email,password=password)
        elif len(password) < 8:
            flash("password must be more than 8 characters!")
            return render_template('register.html', name=name, username=username, email=email,password=password)
        elif not re.search("[a-z]", password):
            flash("password must have small letters!")
            return render_template('register.html', name=name, username=username, email=email,password=password)
        elif not re.search("[A-Z]", password):
            flash("password must have capital letters!")
            return render_template('register.html', name=name, username=username, email=email,password=password)
        elif not re.search("[_@$]+", password):
          flash("Password must contain special characters!")
          return render_template('register.html', name=name, username=username, email=email, password=password)
        else:
            cur.execute("INSERT INTO users(name, username, email, password) VALUES(%s, %s, %s, %s)",
                        (name, username, email, password))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('login'))
    else:
        return render_template('register.html')

#user authenticationf
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
       name=request.form['nm']
       password=request.form['password']

       cur=mysql.connection.cursor()
       cur.execute("SELECT *FROM users WHERE username=%s AND password=%s",(name,password))
       result=cur.fetchone()
       mysql.connection.commit()
       cur.close()

       if result is not None:
          session['username']=name[0]
          flash("log in successfully !")
          return redirect(url_for('welcome'))

       else:
           flash("Invalid username or password !!")
           
    return render_template('login.html')

@app.route('/welcome')
def welcome():
    if "username" in session:
        name=session['username']
        return render_template('welcome.html')
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if "username" in session:
       session.pop('name',None)
       flash("You have been logged out !",'error')
       return redirect(url_for('login'))


@app.route('/forgot',methods=['POST','GET'])
def forgot():
    if request.method=='POST':
        email=request.form['email']
        cur=mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s",(email,))
        result=cur.fetchone()
        if result:
            token=secrets.token_hex(32)
            reset_link=url_for('reset',token=token,_external=True)
            msg=Message(subject='Password Reset Request',sender='laytonmatheka7@gmail.com',recipients=[email])
            msg.body=f'Click the following link to reset your password:{reset_link}'
            mail.send(msg)
            cur=mysql.connection.cursor()
            cur.execute("UPDATE users SET token=%s WHERE email=%s",(token,email))
            mysql.connection.commit()
            cur.close()
            return render_template('forgot.html',success='Reset link has been send to your email')
        else:
            flash("We can't find your email in our system")
            return redirect(url_for('forgot'))
    return render_template('forgot.html')


@app.route('/reset',methods=['POST','GET'])
def reset():
    if request.method=='POST':
        password=request.form['password']
        re_password=request.form['re_password']
        if password!=re_password:
            flash('password do not match')
            return render_template('reset.html',password=password,re_password=re_password)
        elif len(password)<8:
            flash('weak password!')
            return render_template('reset.html',password=password,re_password=re_password)
        elif not re.search("[A-Z]",password):
            flash('Password should include a capital letter')
            return render_template('reset.html',password=password,re_password=re_password)
        elif not re.search("[a-z]",password):
            flash('Password should include a small letter')
            return render_template('reset.html',password=password,re_password=re_password)
        elif not re.search("[_@$]+",password):
            flash('Password should include a special symbol like "_"')
            return render_template('reset.html',password=password,re_password=re_password)
        else:
            if "username" in session:
               cur=mysql.connection.cursor()
               cur.execute("UPDATE users SET password=%s WHERE token=%s",(token,email))
               return render_template('reset.html',success="Password reset successfully")
    return render_template('reset.html')



if __name__=="__main__":
        app.run(debug=True)


