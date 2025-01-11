import os, magic, uuid, hashlib
import psycopg2 as db
from werkzeug.utils import secure_filename
from flask import Flask, session, url_for, render_template, redirect, request, flash, send_from_directory

app = Flask(__name__)
app.secret_key = "#kel1!"
conn = db.connect(database="YOUR_DATABASE", 
                        user="YOUR_USER", 
                        password="YOUR_PASSWORD", 
                        host="YOUR_HOST", 
                        port=1234) # Fill this with your own port.
query = "SELECT * FROM user_cred WHERE email = %s;"
reg_query = "INSERT INTO user_cred VALUES (%s, %s, %s)"
proh_char = set('!@#$%^&*()+=[]{};:\'"<>,.?/|\\~ ')
email_proh_char = set('!#$%^&*()+=[]{};:\'"<>,?/|\\~ ')

# Convert password to hash
def hash_pass(a):
    password = a.encode('utf-8')
    hash_object = hashlib.sha256(password)
    return hash_object.hexdigest()

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# Login page
@app.route("/", methods=["GET", "POST"])
def login():
    if "id" in session:
        return redirect(url_for("dash"))
    elif request.form.get("submit"):
        session["saved-login"] = True if request.form.get('save-login') else False
        session["email"] = request.form['email']
        session["pass"] = hash_pass(request.form['password'])
        session["login-rdr"] = True
        return redirect(url_for("loginrdr"))
    elif request.form.get("register"):
        if any(char in proh_char for char in request.form['username-reg']) or \
            any(char in email_proh_char for char in request.form['email-reg']):
            flash("Username atau email tidak boleh terdapat simbol!")
            return redirect(url_for("login"))    
        else:
            session['email-reg'] = request.form['email-reg']
            session['username-reg'] = request.form['username-reg']
            session['pass-reg'] = hash_pass(request.form['pass-reg'])
            session['reg'] = True
            return redirect(url_for("regist"))
    else:
        return render_template("login.html")
    
# redirect to create user to prevent multiple submitted
@app.route("/regist")
def regist():
    if "reg" in session:
        try:
            with conn.cursor() as curs:
                curs.execute(reg_query, (session['username-reg'], session['email-reg'], session['pass-reg']))
                conn.commit()
                flash("Daftar berhasil, silahkan login!")
                return redirect(url_for("login"))
        except db.Error as e:
            flash(f'Terjadi kesalahan: {e}')
            return redirect(url_for("login"))
        finally:
            session.pop('reg', None)
    else:
        flash("Isi form register terlebih dahulu!")
        return redirect(url_for("login"))

# redirect from login to prevent multiple login
@app.route("/login")
def loginrdr():
    if "login-rdr" in session:
        try:
            with conn.cursor() as curs:
                curs.execute(query, (session["email"],))
                result = curs.fetchone()

            if result is None:
                flash("data tidak ditemukan")
                return redirect(url_for("login"))
            
            if result[2] == session['pass']:
                session.pop("login-rdr", None)
                session.permanent = session["saved-login"]
                session['id'] = result[0]
                return redirect(url_for("dash"))
            else:
                session.pop("login-rdr", None)
                flash("password salah")
                return redirect(url_for("login"))
        except db.Error as e:
            flash(f"Terjadi kesalahan pada sistem. {e}")
            return redirect(url_for("login"))
        finally:
            session.pop("login-rdr", None)
    else:
        return redirect(url_for("login"))

# Dashboard system
@app.route("/dash/upload", methods=["GET", "POST"])
def dash_upload():
    if "id" not in session:
        flash("Anda harus login terlebih dahulu!")
        return redirect(url_for("login"))
    else:
        return render_template("upload.html")

@app.route("/dash", methods=["GET", "POST"])
def dash():
    if "id" not in session:
        flash("Anda harus login terlebih dahulu!")
        return redirect(url_for("login"))
    else:
        return render_template("home.html")

@app.route("/logout")
def logout():
    if "id" in session:
        session.pop("id", None)
        session.permanent = False
        flash("Anda logout")
        return redirect(url_for("login"))    
    else:
        return redirect(url_for("login"))

if __name__ == "__main__":
    app.run()
