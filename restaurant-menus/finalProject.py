import os

from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'just a key key'
db = SQLAlchemy(app)

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    menu_items = db.relationship('MenuItem', backref='restaurant', lazy='dynamic')

    def __repr__(self):
        return '<Restaurant %r>' % self.name

    @staticmethod
    def get_all():
        return Restaurant.query.all()

    @staticmethod
    def query_by_id(id):
        return Restaurant.query.filter_by(id=id).first_or_404()

    def add_and_commit(self):
        db.session.add(self)
        db.session.commit()

    def rename(self, new_name):
        self.name = new_name
        self.add_and_commit()

    def delete(self):
        for item in self.menu_items:
            item.delete()
        db.session.delete(self)
        db.session.commit()


class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Float, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

    def __repr__(self):
        return '<MenuItem %r>' % self.name

    @staticmethod
    def query_by_id(id):
        return MenuItem.query.filter_by(id=id).first_or_404()

    def add_and_commit(self):
        db.session.add(self)
        db.session.commit()

    def rename(self, new_name):
        self.name = new_name
        self.add_and_commit()

    def change_price(self, new_price):
        assert isintance(new_price, float)
        self.price = new_price
        self.add_and_commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class RestaurantForm(FlaskForm):
    name = StringField('Restaurant name', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('Submit')

class MenuItemForm(FlaskForm):
    name = StringField('Item name', validators=[DataRequired(), Length(1, 64)])
    price = FloatField('Price', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/')
@app.route('/restaurants')
def all_restaurants():
    restaurants=Restaurant.get_all()
    return render_template('all_restaurants.html', restaurants=restaurants)

@app.route('/restaurant/new', methods=['GET', 'POST'])
def new_restaurant():
    form = RestaurantForm()
    if form.validate_on_submit():
        restaurant = Restaurant(name=form.name.data)
        restaurant.add_and_commit()
        return redirect(url_for('all_restaurants'))
    return render_template('new_restaurant.html', form=form)

@app.route('/restaurant/rename/<int:restaurant_id>', methods=['GET', 'POST'])
def rename_restaurant(restaurant_id):
    form = RestaurantForm()
    restaurant = Restaurant.query_by_id(restaurant_id)
    if form.validate_on_submit():
        restaurant.rename(form.name.data)
        return redirect(url_for('all_restaurants'))
    return render_template('rename_restaurant.html', restaurant=restaurant, form=form)

@app.route('/restaurant/delete/<int:restaurant_id>')
def delete_restaurant(restaurant_id):
    restaurant = Restaurant.query_by_id(restaurant_id)
    restaurant.delete()
    return redirect(url_for('all_restaurants'))

@app.route('/restaurant/<int:restaurant_id>')
def restaurant(restaurant_id):
    restaurant = Restaurant.query_by_id(restaurant_id)
    return render_template('restaurant.html', restaurant=restaurant)

@app.route('/mitem/new/<int:restaurant_id>', methods=['GET', 'POST'])
def new_menu_item(restaurant_id):
    restaurant = Restaurant.query_by_id(restaurant_id)
    form = MenuItemForm()
    if form.validate_on_submit():
        item = MenuItem(name=form.name.data, price=form.price.data,
                restaurant_id=restaurant_id)
        item.add_and_commit()
        return redirect(url_for('restaurant', restaurant_id=restaurant_id))
    return render_template('new_menu_item.html', restaurant=restaurant, form=form)

@app.route('/mitem/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_menu_item(item_id):
    menu_item = MenuItem.query_by_id(item_id)
    form = MenuItemForm()
    if form.validate_on_submit():
        menu_item.name = form.name.data
        menu_item.price = form.price.data
        menu_item.add_and_commit()
        return redirect(url_for('restaurant', restaurant_id=menu_item.restaurant_id))
    else:
        form.name.data = menu_item.name
        form.price.data = menu_item.price
        return render_template('edit_menu_item.html', form=form)

@app.route('/mitem/delete/<int:item_id>')
def delete_menu_item(item_id):
    menu_item = MenuItem.query_by_id(item_id)
    menu_item.delete()
    return redirect(url_for('restaurant', restaurant_id=menu_item.restaurant_id))


if __name__ == '__main__':
    app.debug = True
    db.create_all()
    app.run()
