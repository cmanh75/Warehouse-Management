from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from form import RegisterForm, LoginForm, UploadForm
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os


class Base(DeclarativeBase):
    pass
app = Flask(__name__)
app.config['SECRET_KEY'] = "cmanh75deptrai"
Bootstrap5(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str]= mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            email=request.form.get("email"),
            name=request.form.get("name"),
            password=request.form.get("password")
        )
        check_exist = db.session.execute(db.select(User).where(User.email == new_user.email)).scalar
        if check_exist:
            return render_template('register.html', form=form, existed=True)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html', form=form, existed=False)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        account = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        if account and account.password == form.password.data:
            login_user(account)
            return redirect(url_for('home'))
        return render_template('login.html', form=form, valid=True)
    return render_template('login.html', form=form, valid=False)

@app.route('/add', methods=["POST", "GET"])
def add():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.image.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(app._static_folder, 'assets\\img', filename)) 
        return redirect(url_for('home'))
    return render_template('add.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
