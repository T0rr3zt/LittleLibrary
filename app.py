from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, HiddenField  # Added HiddenField
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
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def __repr__(self):
        return f'<LittleLibrary {self.name}>'

# Forms
# class LibraryForm(FlaskForm):
#     name = StringField('Library Name', validators=[DataRequired()])
#     address = StringField('Address', validators=[DataRequired()])  # Make sure this exists
#     city = StringField('City', validators=[DataRequired()])
#     state = StringField('State (2-letter code)', validators=[DataRequired()])
#     zip_code = StringField('ZIP Code', validators=[DataRequired()])
#     description = TextAreaField('Description')
#     submit = SubmitField('Add Library')



class LibraryForm(FlaskForm):
    name = StringField('Library Name', validators=[DataRequired()])
    latitude = HiddenField('Latitude', validators=[DataRequired()])
    longitude = HiddenField('Longitude', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Add Library')



# Routes
# @app.route('/')
# def index():
#     return render_template('index.html')


@app.route('/')
def index():
    form = LibraryForm()
    libraries = LittleLibrary.query.all()
    return render_template('index.html', form=form, libraries=libraries)

@app.route('/libraries')
def libraries():
    libraries = LittleLibrary.query.all()
    return render_template('libraries.html', libraries=libraries)

# @app.route('/add', methods=['GET', 'POST'])
# def add_library():
#     form = LibraryForm()
#     if form.validate_on_submit():
#         # Here you would add geocoding logic to get lat/long from address
#         library = LittleLibrary(
#             name=form.name.data,
#             address=form.address.data,
#             city=form.city.data,
#             state=form.state.data,
#             zip_code=form.zip_code.data,
#             description=form.description.data,
#             # For now, we'll leave lat/long as None
#             # In a production app, you'd use geopy or similar to geocode
#         )
#         db.session.add(library)
#         db.session.commit()
#         flash('Library added successfully!', 'success')
#         return redirect(url_for('libraries'))
#     return render_template('add_library.html', form=form)

@app.route('/add', methods=['GET', 'POST'])
def add_library():
    form = LibraryForm()
    if form.validate_on_submit():
        # Geocode the coordinates to get address details
        try:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="little_libraries")
            location = geolocator.reverse(f"{form.latitude.data}, {form.longitude.data}")
            
            library = LittleLibrary(
                name=form.name.data,
                latitude=form.latitude.data,
                longitude=form.longitude.data,
                description=form.description.data,
                address=location.address.split(',')[0] if location else "Unknown",
                city=location.raw.get('address', {}).get('city', '') if location else "Unknown",
                state=location.raw.get('address', {}).get('state', '') if location else "Unknown",
                zip_code=location.raw.get('address', {}).get('postcode', '') if location else "Unknown"
            )
            db.session.add(library)
            db.session.commit()
            flash('Library added successfully!', 'success')
            return jsonify({'success': True}) if request.is_json else redirect(url_for('index'))
        except Exception as e:
            flash(f'Error adding library: {str(e)}', 'danger')
            return jsonify({'success': False, 'error': str(e)}) if request.is_json else redirect(url_for('index'))
    
    # Handle AJAX requests differently
    if request.method == 'POST' and request.is_json:
        return jsonify({'success': False, 'errors': form.errors})
    
    return render_template('index.html', form=form, libraries=LittleLibrary.query.all())


@app.route('/library/<int:id>')
def library_detail(id):
    library = LittleLibrary.query.get_or_404(id)
    return render_template('library_detail.html', library=library)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)