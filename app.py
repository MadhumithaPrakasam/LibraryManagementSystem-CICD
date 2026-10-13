import os, sqlite3
from pathlib import Path
from flask import Flask, g, request, redirect, url_for, render_template, flash

def create_app(config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY=os.getenv("SECRET_KEY", "classroom-demo"),
                      DATABASE=os.getenv("LIBRARY_DB_PATH", "data/library.db"))
    if config: app.config.update(config)
    def db():
        if "db" not in g:
            p = Path(app.config["DATABASE"]); p.parent.mkdir(parents=True, exist_ok=True)
            g.db = sqlite3.connect(p); g.db.row_factory = sqlite3.Row
            g.db.executescript('''
                CREATE TABLE IF NOT EXISTS books(id INTEGER PRIMARY KEY, title TEXT NOT NULL, author TEXT NOT NULL, isbn TEXT UNIQUE, total INTEGER NOT NULL, available INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS members(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL);
                CREATE TABLE IF NOT EXISTS loans(id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL, member_id INTEGER NOT NULL, issue_date TEXT DEFAULT CURRENT_DATE, return_date TEXT);
            '''); g.db.commit()
        return g.db
    @app.teardown_appcontext
    def close(error=None):
        c=g.pop("db",None)
        if c: c.close()
    @app.get("/")
    def home():
        c=db()
        stats={"titles":c.execute("SELECT COUNT(*) FROM books").fetchone()[0],
               "copies":c.execute("SELECT COALESCE(SUM(available),0) FROM books").fetchone()[0],
               "members":c.execute("SELECT COUNT(*) FROM members").fetchone()[0],
               "issued":c.execute("SELECT COUNT(*) FROM loans WHERE return_date IS NULL").fetchone()[0]}
        return render_template("index.html",books=c.execute("SELECT * FROM books ORDER BY title").fetchall(),stats=stats)
    @app.get("/health")
    def health(): return {"status":"ok"},200
    @app.post("/books")
    def add_book():
        title=request.form.get("title","").strip(); author=request.form.get("author","").strip()
        isbn=request.form.get("isbn","").strip() or None
        try: copies=int(request.form.get("copies","1")); assert title and author and copies>0
        except (ValueError, AssertionError):
            flash("Enter a title, author, and at least one copy.","error"); return redirect(url_for("home"))
        try:
            c=db(); c.execute("INSERT INTO books(title,author,isbn,total,available) VALUES(?,?,?,?,?)",(title,author,isbn,copies,copies)); c.commit()
            flash("Book added.","success")
        except sqlite3.IntegrityError: flash("ISBN already exists.","error")
        return redirect(url_for("home"))
    @app.post("/members")
    def add_member():
        name=request.form.get("name","").strip(); email=request.form.get("email","").strip()
        if not name or "@" not in email: flash("Enter a valid name and email.","error")
        else:
            try: c=db(); c.execute("INSERT INTO members(name,email) VALUES(?,?)",(name,email)); c.commit(); flash("Member registered.","success")
            except sqlite3.IntegrityError: flash("Email already registered.","error")
        return redirect(url_for("home"))
    @app.get("/members")
    def members(): return render_template("members.html",members=db().execute("SELECT * FROM members ORDER BY name").fetchall())
    @app.post("/issue/<int:book_id>")
    def issue(book_id):
        c=db(); mid=request.form.get("member_id",type=int); b=c.execute("SELECT * FROM books WHERE id=?",(book_id,)).fetchone()
        m=c.execute("SELECT * FROM members WHERE id=?",(mid,)).fetchone() if mid else None
        if not b or not m: flash("Choose a valid member and book.","error")
        elif b["available"]<1: flash("No copies available.","error")
        else: c.execute("INSERT INTO loans(book_id,member_id) VALUES(?,?)",(book_id,mid)); c.execute("UPDATE books SET available=available-1 WHERE id=?",(book_id,)); c.commit(); flash("Book issued.","success")
        return redirect(url_for("home"))
    @app.get("/loans")
    def loans():
        rows=db().execute("SELECT loans.*,books.title,members.name FROM loans JOIN books ON books.id=loans.book_id JOIN members ON members.id=loans.member_id ORDER BY loans.id DESC").fetchall()
        return render_template("loans.html",loans=rows)
    @app.post("/return/<int:loan_id>")
    def return_book(loan_id):
        c=db(); loan=c.execute("SELECT * FROM loans WHERE id=?",(loan_id,)).fetchone()
        if not loan: flash("Loan not found.","error")
        elif loan["return_date"]: flash("Already returned.","error")
        else: c.execute("UPDATE loans SET return_date=CURRENT_DATE WHERE id=?",(loan_id,)); c.execute("UPDATE books SET available=available+1 WHERE id=?",(loan["book_id"],)); c.commit(); flash("Book returned.","success")
        return redirect(url_for("loans"))
    return app
app=create_app()
if __name__=="__main__": app.run(host="0.0.0.0",port=5000)
