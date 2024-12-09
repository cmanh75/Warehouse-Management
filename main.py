from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean
from form import RegisterForm, LoginForm, UploadForm, CheckoutForm, PlaceOrder, Confirm, ImportForm
from flask_bootstrap import Bootstrap5
from typing import List, Optional
from functools import wraps
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from datetime import datetime as dt, timedelta
from dotenv import load_dotenv
import locale
import os
import pandas as pd
import matplotlib.pyplot as plt

load_dotenv()

class Base(DeclarativeBase):
    pass
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ["secret_key"]
Bootstrap5(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(model_class=Base)
ckeditor = CKEditor(app)
db.init_app(app)
locale.setlocale(locale.LC_ALL, '')
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str]= mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    selections = relationship("Selection", back_populates="user")
    address: Mapped[Optional[str]] = mapped_column(String)
    shipping: Mapped[Optional[str]] = mapped_column(String)
    total_price: Mapped[Optional[str]] = mapped_column(String)
    summary: Mapped[Optional[str]] = mapped_column(String)
    delivery_date: Mapped[Optional[str]] = mapped_column(String)

class Product(db.Model):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    img_path: Mapped[str] = mapped_column(String, nullable=False)
    selections = relationship("Selection", back_populates="product")

class Selection(db.Model):
    __tablename__ = "selections"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("products.id"))
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    user = relationship("User", back_populates="selections")
    product = relationship("Product", back_populates="selections")
    order_id: Mapped[Optional[int]] = mapped_column(db.ForeignKey("orders.id"))
    order: Mapped[Optional["Order"]] = relationship(back_populates="selections")

class Order(db.Model):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"))
    user = relationship("User")
    selections: Mapped[List["Selection"]] = relationship(back_populates="order")
    order_date: Mapped[str] = mapped_column(String, nullable=False)
    confirmed: Mapped[Optional[bool]] = mapped_column(Boolean)
    feedback: Mapped[Optional[str]] = mapped_column(String)

with app.app_context():
    db.create_all()

@app.route('/add_to_cart', methods=["POST", "PATCH", "GET"])
def add_to_cart():
    product_id = request.args.get("product_id")
    product = db.session.execute(db.select(Product).where(Product.id == product_id)).scalar()
    check_exist = db.session.execute(db.select(Selection).where((Selection.product_id == product_id), (Selection.user_id == current_user.id))).scalar()
    print(request.form.get('name'))
    if request.method == "POST":
        print(122)
    if check_exist:
        check_exist.quantity += 1
        db.session.commit()
    else:
        new_item = Selection(
            product_id=product.id,
            user_id = current_user.id,
            quantity = 1,
            user = current_user,
            product = product
        )
        db.session.add(new_item)
        db.session.commit()
    return redirect(url_for('checkout'))

def currency_format(x):
    if x < 0:
        x = -x
        return "-" +locale.currency(x, grouping=True)[:-3].strip('$') + "₫"
    return locale.currency(x, grouping=True)[:-3].strip('$') + "₫"

@app.route('/show_order', methods=["PUT", "PATCH", "GET", "POST"])
@login_required
def show_order():
    form = Confirm()
    order_id = request.args.get("order_id")
    order = db.session.execute(db.select(Order).where(Order.id == order_id)).scalar()
    if request.method == "POST":
        order.feedback = form.feedback.data
        order.confirmed = False
        if form.accept.data:
            df = pd.read_csv("static/assets/revenue.csv")
            for each in order.selections:
                each.product.number -= each.quantity
            print(df.columns)
            revenue = df.tail(1)['REVENUE'].values[0]
            revenue += int(order.selections[0].user.summary.strip("₫").replace(",", ""))
            new_row = pd.DataFrame({
                'TIME': [dt.now().strftime("%Y-%m-%d %H:%M")],
                'REVENUE': [revenue]
            })
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv("static/assets/revenue.csv", index=False)
            order.confirmed = True
        db.session.commit()
    return render_template("show_order.html", order=order, form=form)

@app.route('/statistic')
def statistic():
    df = pd.read_csv("static/assets/revenue.csv")
    df = df.iloc[::-1]
    for index, row in df.iterrows():
        df.at[index, 'REVENUE'] = currency_format(row['REVENUE'])
    return render_template("statistic.html", df=df)

@app.route('/')
def home():
    df = pd.read_csv("static/assets/products.csv")
    # for (index, data_row) in df.iterrows():
    #     new_product = Product(
    #         id=data_row["ID"],
    #         name=data_row["NAME"],
    #         number=data_row["NUMBER"],
    #         price=currency_format((data_row["PRICE"]) * 10000),
    #         img_path=f'static\\assets\\img\\{data_row["IMG_PATH"]}'
    #     )
    #     db.session.add(new_product)
    #     db.session.commit()
    return render_template('index.html')

@app.route('/manage')
def manage():
    list = db.session.execute(db.select(Order)).scalars().all()
    return render_template('manage.html', list=list)

@app.route('/history', methods=["POST", "GET"])
def history():
    list = db.session.execute(db.select(Order).where(Order.user_id == current_user.id)).scalars().all()
    return render_template('history.html', list=list)

@app.route('/checkout', methods=["POST", "GET", "PATCH", "PUT"])
def checkout():
    if not current_user.is_authenticated:
        flash('Please login')
        return redirect(url_for('login'))
    list = db.session.execute(db.select(Selection).where(Selection.user_id == current_user.id)).scalars().all()
    order_form = CheckoutForm()
    place_order = PlaceOrder()
    user = db.session.execute(db.select(User).where(User.id == current_user.id)).scalar()
    if order_form.submit.data and order_form.validate():
        user.address = order_form.address.data
        print(order_form.address.data)
        days = 1
        shipping = 50000
        if order_form.delivery_options.data == '2':
            days = 3
            shipping = 30000
        if order_form.delivery_options.data == '3':
            days = 5
            shipping = 20000
        user.delivery_date = (dt.now() + timedelta(days=days)).strftime("%B %d, %Y")
        total_price = 0
        for each in list:
            total_price += int(locale.atof(each.product.price.strip('₫'))) * each.quantity
        user.total_price = currency_format(total_price)
        print(total_price)
        user.summary = currency_format(total_price + shipping)
        user.shipping = currency_format(shipping)
        db.session.commit()
        return render_template("checkout.html", _list=list, filled=True, user=user, order_form=order_form, place_order=place_order)
    order_form.address.data = user.address
    if place_order.submit.data and place_order.validate():
        order = Order(
            selections=list,
            user_id=current_user.id,
            user=current_user,
            order_date=dt.now().strftime("%B %d, %Y"),
        )
        db.session.add(order)
        db.session.commit()
        return redirect('history')
    return render_template('checkout.html', _list=list, filled=False, user=None, order_form=order_form, place_order=place_order)

@app.route('/imported', methods=["GET", "POST", "PATCH"])
def imported():
    product_id = request.args.get("product_id")
    total = request.args.get("total")
    df = pd.read_csv("static/assets/revenue.csv")
    revenue = df.tail(1)['REVENUE'].values[0]
    revenue -= int(total.strip('₫').replace(",", "")) * 0.9
    new_row = pd.DataFrame({
        'TIME': [dt.now().strftime("%Y-%m-%d %H:%M")],
        'REVENUE': [revenue]
    })
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv("static/assets/revenue.csv", index=False)
    product = db.session.execute(db.select(Product).where(Product.id == product_id)).scalar()
    product.number += int(request.args.get("quantity"))
    db.session.commit()
    return redirect(url_for('products'))

@app.route('/import', methods=["POST", "GET"])
def import_pd():
    form = ImportForm()
    confirmed = False
    product_id = request.args.get("product_id")
    product = db.session.execute(db.select(Product).where(Product.id == product_id)).scalar()
    quantity = 0
    total = 0
    description = ""
    if request.method == "POST":
        description = form.description.data
        quantity = int(form.quantity.data)
        total = int(product.price.strip("₫").replace(",", "")) * int(form.quantity.data) * 0.9
        confirmed = True
    return render_template('import.html', product=product, form=form, confirmed=confirmed, total=currency_format(total), quantity=quantity, description=description)

@app.route('/delete-item', methods=["GET", "DELETE"])
def delete_item():
    db.session.delete(db.session.execute(db.select(Selection).where(Selection.id == int(request.args.get("item_id")))).scalar())
    db.session.commit()
    return redirect(url_for('checkout'))

@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            email=request.form.get("email"),
            name=request.form.get("name"),
            password=request.form.get("password")
        )
        check_exist = db.session.execute(db.select(User).where(User.email == new_user.email)).scalar()
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

@app.route('/edit', methods=["GET", "POST", "PUT"])
def edit():
    print(1)
    form = UploadForm()
    if form.validate_on_submit():
        print(1)
        product = db.session.execute(db.select(Product).where(Product.id == request.args.get("product_id"))).scalar()
        f = form.image.data
        filename = secure_filename(f.filename)
        path = os.path.join(app._static_folder, 'assets\\img', filename)
        product.name = form.name.data
        product.price = currency_format(int(form.price.data))
        product.img_path = path
        product.number = form.number.data
        f.save(path)
        db.session.commit()
        return redirect(url_for('products'))
    return render_template('add.html', form=form)

@app.route('/add', methods=["POST", "GET"])
def add():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.image.data
        filename = secure_filename(f.filename)
        path = os.path.join(app._static_folder, 'assets\\img', filename)
        new_product = Product(
            name=form.name.data,
            price=currency_format(int(form.price.data)),
            img_path=path,
            number=form.number.data
        )
        db.session.add(new_product)
        db.session.commit()
        f.save(path) 
        return redirect(url_for('home'))
    return render_template('add.html', form=form)

@app.route('/about')
def about():
    return render_template('contact.html')

@app.route('/find', methods=["GET", "POST"])
def find():
    if request.method == "POST":
        name = request.form.get("name")
        list = db.session.execute(db.select(Product)).scalars().all()
        new_list = []
        for each in list:
            if name.lower() in each.name.lower():
                print(each.name)
                new_list.append(each)
        return render_template('products.html', list=new_list)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/products')
def products():
    list = db.session.execute(db.select(Product)).scalars().all()
    return render_template('products.html', list=list)

if __name__ == '__main__':
    app.run(debug=True)
