
#import os

from flask import Flask, render_template, request, flash, redirect, session  
import requests
from flask_debugtoolbar import DebugToolbarExtension


#from sqlalchemy.exc import IntegrityError

from forms import UserForm 

from models import db, connect_db, City, User, Info 

#API_BASE_URL = 'https://api.spoonacular.com/recipes/complexSearch?'

#apiKey = 'apiKey=287b42f8924842a8b692c3ee9b00c469'




app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///wheather_map'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "it's a secret"

toolbar = DebugToolbarExtension(app)

connect_db(app)





#############Menu Tables####################################################
@app.route("/")
def homepage():
    """Render homepage."""

    return render_template("Homepage.html")

@app.route("/sign_up", methods=['GET', 'POST'])
def sign_up_form():
    """Render sign_up_form."""
    form= UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        new_user = User.register(username, password)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        flash('Welcome! You have successfully created your account!', "success")
    
        return redirect('/info')
    
    return render_template("sign_up_form.html", form=form)




@app.route("/log_in", methods=['GET','Post'])
def log_in_form():
    """Render log_in_form."""
    form= UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "success")
            session['user_id'] = user.id 
            return redirect('/wheather_page')
        else:
            form.username.errors = ['Invalid username/paswword.']   
    
    return render_template("log_in_form.html", form=form)   


@app.route("/log_out")
def log_out_form():
    """Render log_out_form."""
    session.pop('user_id')
    return render_template("log_out_page.html")

@app.route("/wheather_page", methods=['GET', 'POST'])
def application_form():
    """Render Weather page."""
    if "user_id" not in session:
        flash('You are not logged in. Please log in.', "danger")
        return redirect('/')
    
       
    if request.method == 'POST':
        new_city = request.form.get('city')

        if new_city:
            new_city_obj = City(name=new_city)

            db.session.add(new_city_obj)
            db.session.commit()
    cities = City.query.all() 
    
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=becab9b25495075465e7cedcd8e003ae'
    

    weather_data = []

    for city in cities:
        res = requests.get(url.format(city.name)).json()
    

        weather = {
            'city' : city.name,
            'temperature' :  res['main']['temp'],
            'description' :  res['weather'][0]['description'],
            'icon' : res['weather'][0]['icon'],
        }

        weather_data.append(weather)

   
    return render_template("Wheather_Page.html", weather_data=weather_data)
    
 
 
 ########################################################
@app.route("/info", methods=['GET', 'POST'])
def info_page():
    """Render info_page"""
       
    
    infos = Info.query.all()  
   
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    job_description = request.form.get("job_description")
    reason = request.form.get("type_of_restaurant")

    new_info = Info( first_name=first_name, last_name=last_name, job_description=job_description, reason=reason, user_id=session['user_id'])
    
    
    db.session.add(new_info)
    db.session.commit()
    
    flash('Thank you for your infomation. Click the weather link to find the weather in your city', "success")
    return render_template("info.html", first_name=first_name,
                                                   last_name=last_name,   
                                                   job_description=job_description,
                                                   reason=reason)
                                                   

    
 
 
 
 #infos = Info.query.all()  
    
    #owners_first_name = request.form.get("owners_first_name")
    #owners_last_name = request.form.get("owners_last_name")
    #restaurant_name = request.form.get("restaurant_name")
    #type_of_restaurant = request.form.get("type_of_restaurant")

    #new_info = Info(owners_first_name=owners_first_name, owners_last_name=owners_last_name, 
                                                              #restaurant_name=restaurant_name, 
                                                              #type_of_restaurant=type_of_restaurant, 
                                                              #user_id=session['user_id'])
    #db.session.add(new_info)
    #db.session.commit()
    ##return redirect('/welcomebackpage')
    #flash('Thank you for your infomation. Click the Application link to complete your menu', "success")
    #return render_template("info.html", owners_first_name=owners_first_name,
                                                   #owners_last_name=owners_last_name,   
                                                   #restaurant_name=restaurant_name,
                                                   #type_of_restaurant=type_of_restaurant)
                                                   ##infos=infos)
