from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SubmitField
from wtforms.validators import DataRequired
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)  # Add this line to ensure instance folder exists
db = SQLAlchemy(app)

# Database Models
class LittleLibrary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    description = db.Column(db.Text)
    added_by = db.Column(db.String(100))

    def __repr__(self):
        return f'<LittleLibrary {self.name}>'

# Forms
class LibraryForm(FlaskForm):
    name = StringField('Library Name', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State (2-letter code)', validators=[DataRequired()])
    zip_code = StringField('ZIP Code', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Add Library')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/libraries')
def libraries():
    libraries = LittleLibrary.query.all()
    return render_template('libraries.html', libraries=libraries)

@app.route('/add', methods=['GET', 'POST'])
def add_library():
    form = LibraryForm()
    if form.validate_on_submit():
        # Here you would add geocoding logic to get lat/long from address
        library = LittleLibrary(
            name=form.name.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip_code=form.zip_code.data,
            description=form.description.data,
            # For now, we'll leave lat/long as None
            # In a production app, you'd use geopy or similar to geocode
        )
        db.session.add(library)
        db.session.commit()
        flash('Library added successfully!', 'success')
        return redirect(url_for('libraries'))
    return render_template('add_library.html', form=form)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)