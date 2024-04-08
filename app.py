from flask import Flask, render_template, request, redirect, session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "3svyNhBp#q@tw@vLtkVNy)%z"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///billing.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"{self.id} - {self.name}"
    

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), default="")
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"{self.id} - {self.name}"


@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        data = User.query.filter_by(email=email, password=password).first()

        if(data is not None):

            session['uid'] = data.id

            if(data.type == "Admin"):
                product_data = Product.query.all()
                return render_template('index.html', product_data=product_data, user_data=data)
            else:
                return render_template('user.html', user_data=data)
        else:
            return {
                "status": 404,
                "msg": "No User Found"
            }

    return render_template('login.html')


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():

    if request.method == 'POST':
        email = request.form['email']
        data = User.query.filter_by(email=email).first()

        if(data is not None):
            return {
                "status": 101,
                "msg": "User already exist with same email"
            }
        else:
            type = request.form['type']
            name = request.form['name']
            password = request.form['password']
            data = User(type=type, name=name, email=email, password=password)
            db.session.add(data)
            db.session.commit()

            return render_template('login.html')


    return render_template('register.html')


@app.route('/index', methods=['GET', 'POST'])
def index():

    if 'uid' not in session:
        return redirect("/")
    else:

        id = session['uid']
        user_data = User.query.filter_by(id=id).first()
        product_data = Product.query.all()
        return render_template('index.html', product_data=product_data, user_data=user_data)

    

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():

    if 'uid' not in session:
        return redirect("/")
    else:

        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            description = request.form['description']
            product = Product(name=name, price=price, description=description)
            db.session.add(product)
            db.session.commit()

        return redirect("/index")


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):

    if 'uid' not in session:
        return redirect("/")
    else:

        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            description = request.form['description']
            product = Product(name=name, price=price, description=description)
            product.name = name
            product.price = price
            db.session.add(product)
            db.session.commit()

            return redirect("/index")
    
        product_data = Product.query.filter_by(id=id).first()
        return render_template('update.html', product_data=product_data)

@app.route('/delete/<int:id>')
def delete(id):

    if 'uid' not in session:
        return redirect("/")
    else:

        data = Product.query.filter_by(id=id).first()
        db.session.delete(data)
        db.session.commit()

        return redirect("/index")
    
@app.route('/logout')
def logout():

    session.pop('uid', None)
    return redirect("/")



if __name__ == "__main__":
    app.run(debug=True)