#!usr/bin/python

from flask import Flask , render_template , request , redirect , session , abort , url_for , g , flash 
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager , login_user  , login_required , logout_user , current_user 
from werkzeug.security import generate_password_hash, check_password_hash
# from sqlalchemy.sql import text
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import create_engine

# Models
# Flask app intitialization 

app = Flask(__name__)
app.config.from_pyfile('config.py')

# SQLAlchemy initialization 
import MySQLdb
db = SQLAlchemy(app)

from models import login_model

# # Flask Login Initiialization 

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Base route 
@app.route('/' , methods = ['GET' , 'POST'])
@login_required
def index():
    user = current_user.username 
    return render_template('base.html' , user = user) , 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    """
    form = login_model.LoginForm()
    mssg = ""

    if form.validate_on_submit():
        user = login_model.User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)

                return redirect(url_for('index'))
            else:
                return render_template('login.html', subtitle="Login", form=form, error_mssg="Invalid Username or Password")
        else:
            return render_template('login.html', subtitle="Login", form=form, error_mssg="Invalid Username or Password")
    return render_template('login.html', subtitle="Login", form=form, error_mssg=mssg), 200


@app.route('/signup' , methods=['GET', 'POST'])
def signup():
    form = login_model.SignupForm()
    mssg = ""
    if form.validate_on_submit():
        user = login_model.User.query.filter_by(email = form.email.data).first()
        if user is None:
            hashed_pass = generate_password_hash(form.password.data , method='sha256')
            new_user = login_model.User(username = form.username.data , email = form.email.data , password = hashed_pass)
            # user_table = UserTableCreator(form.email.data)
            # Base.metadata.create_all(engine)        
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return render_template('signup.html' , form = form ,subtitle = "Signup" ,error_mssg = "Email already exists.")

    return render_template('signup.html' , subtitle = "Signup" , form = form , error_mssg = mssg),200

@app.route('/forgot' , methods=['GET', 'POST'])
def forgot():
    return render_template('login.html' , subtitle = "Forgot"),200


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    return login_model.User.query.get(int(user_id))

# Function Routes

@app.route('/contacts' , methods=['GET' , 'POST'])
@login_required
def contacts():
    '''
        Add contacts to database with option to export 
        and import data onto Peep.
    '''
    user = current_user.username 
    form = login_model.AddContact()
    mssg = ""

    return render_template('contacts.html' , user = user) , 200

@app.route('/insights' , methods=['GET' , 'POST'])
@login_required
def insights():
    '''
        Get insights based of various filters 
            - Period
            - Business Category
            - Product dealing IN
            - City
            - State
            - Country
            - Customer Credit Health
            - broker
            - preffered Comm channel
            - no of times comm done
            - No fo Invoice
            - Sales for that user
    '''
    pass


@app.route('/basic_master' , methods=['GET' , 'POST'])
@login_required
def basic_master():
    '''
        Basic master setup done here
    '''
    mssg = ""
    user = current_user.username 
    form_broker = login_model.BrokerForm()
    form_comm = login_model.CommChannelForm()
    form_health = login_model.HealthCodeForm()
    form_prod = login_model.ProdCatForm()
    form_buss = login_model.BussCatForm()
    form_state = login_model.StateForm()
    form_country = login_model.CountryForm()
    form_city = login_model.CityForm()

    prod_list = db.session.query(login_model.ProdCat).all()
    health_list = db.session.query(login_model.HealthCode).all()
    commlist = db.session.query(login_model.CommChannel).all()
    busslist = db.session.query(login_model.BussCat).all()
    broklist = db.session.query(login_model.Broker).all()
    statelist = db.session.query(login_model.State).all()
    countrylist = db.session.query(login_model.Country).all()
    citylist = db.session.query(login_model.City).all()

    
    # Form choices for select fields

    if form_comm.validate_on_submit():
        # Checks for Comm submit 
        mssg = ""
        session['is_checked'] = 'd'
        prod = login_model.CommChannel.query.filter_by(channel=form_comm.channel.data).first()
        if prod :
            mssg = "Duplicate Data "
            return redirect(url_for('basic_master'))

        else:
            new_data = login_model.CommChannel(channel=form_comm.channel.data.upper())  
            try:
                db.session.add(new_data)
                db.session.commit()
                mssg = "Data Successfully added 👍"
                return redirect(url_for('basic_master'))

            
            except Exception as e:
                mssg = "Error occured while adding data 😵. Here's the error : "+str(e)
                return redirect(url_for('basic_master'))


    if form_health.validate_on_submit():
        # Checks for health code submit
        session['is_checked'] = 'b'
        mssg = ""
        prod = login_model.HealthCode.query.filter_by(health=form_health.health.data).first()
        if prod :
            mssg = "Duplicate Data "
            return redirect(url_for('basic_master'))

        else:
            new_data = login_model.HealthCode(health=form_health.health.data.upper())  
            try:
                db.session.add(new_data)
                db.session.commit()
                mssg = "Data Successfully added 👍"
                return redirect(url_for('basic_master'))

            
            except Exception as e:
                mssg = "Error occured while adding data 😵. Here's the error : "+str(e)
                return redirect(url_for('basic_master'))

    if form_prod.validate_on_submit():
        mssg = ""
        session['is_checked'] = 'a'
        prod = login_model.ProdCat.query.filter_by(prod_cat=form_prod.prod_cat.data).first()

        if prod :
            mssg = "Duplicate Data "
            return redirect(url_for('basic_master'))

        else:
            new_data = login_model.ProdCat(prod_cat = form_prod.prod_cat.data.upper())  
            try:
                db.session.add(new_data)
                db.session.commit()
                mssg = "Data Successfully added 👍"
                return redirect(url_for('basic_master'))

            
            except Exception as e:
                mssg = "Error occured while adding data 😵. Here's the error : "+str(e)
                return redirect(url_for('basic_master'))

    if form_buss.validate_on_submit():
        # Checks for Bussiness Category submit
        session['is_checked'] = 'e'
        mssg = ""
        prod = login_model.BussCat.query.filter_by(buss_cat=form_buss.buss_cat.data).first()

        if prod :
            mssg = "Duplicate Data "
            return redirect(url_for('basic_master'))

        else:
            new_data = login_model.BussCat(buss_cat = form_buss.buss_cat.data.upper())  
            try:
                db.session.add(new_data)
                db.session.commit()
                mssg = "Data Successfully added 👍"
                return redirect(url_for('basic_master'))

            
            except Exception as e:
                mssg = "Error occured while adding data 😵. Here's the error : "+str(e)
                return redirect(url_for('basic_master'))

    if form_state.validate_on_submit():
        # Checks for Location submit
        session['is_checked'] = 'f'
        mssg = ""
        prod = login_model.State.query.filter_by(state=form_state.state.data).first()

        if prod :
            mssg = "Duplicate Data "
            return redirect(url_for('basic_master'))

        else:
            new_data = login_model.State(state=form_state.state.data.upper())  
            try:
                db.session.add(new_data)
                db.session.commit()
                mssg = "Data Successfully added 👍"
                return redirect(url_for('basic_master'))

            
            except Exception as e:
                mssg = "Error occured while adding data 😵. Here's the error : "+str(e)
                return redirect(url_for('basic_master'))

    if form_country.validate_on_submit():
        # Checks for Location submit
        session['is_checked'] = 'g'
        mssg = ""
        prod = login_model.Country.query.filter_by(country=form_country.country.data).first()

        if prod :
            mssg = "Duplicate Data "
            return redirect(url_for('basic_master'))

        else:
            new_data = login_model.Country(country=form_country.country.data.upper())  
            try:
                db.session.add(new_data)
                db.session.commit()
                mssg = "Data Successfully added 👍"
                return redirect(url_for('basic_master'))

            
            except Exception as e:
                mssg = "Error occured while adding data 😵. Here's the error : "+str(e)
                return redirect(url_for('basic_master'))
    

    return render_template('basic_master.html' , user = user , 
        form_broker = form_broker , form_buss = form_buss , form_comm = form_comm ,
        form_health = form_health , form_state = form_state , form_prod = form_prod ,
        form_country = form_country , form_city = form_city , error_mssg = mssg ,
        subtitle = "Basic Master" , plist = prod_list , hlist = health_list ,
        commlist = commlist , busslist = busslist , broklist = broklist ,
        statelist = statelist , countrylist = countrylist , citylist = citylist) , 200


@app.route('/city_form' , methods= ['GET' , 'POST'])
def city_form():
    # UP : Work on securing this route
    session['is_checked'] = 'h'
    prod = login_model.City.query.filter_by(city=request.form['city']).first()
    if prod :
            mssg = "Duplicate Data "
            return redirect(url_for('basic_master'))
    else:
        state = login_model.State.query.filter_by(id=int(request.form['state'])).first().state
        country = login_model.Country.query.filter_by(id=int(request.form['country'])).first().country
        new_data = login_model.City(city=request.form['city'].upper() , state = state ,
        country = country ) 

        try:
            db.session.add(new_data)
            db.session.commit()
            mssg = "Data Successfully added 👍"
            return redirect(url_for('basic_master'))


        except Exception as e:
            mssg = "Error occured while adding data 😵. Here's the error : "+str(e)
            return redirect(url_for('basic_master'))

@app.route('/broker_form' , methods= ['GET' , 'POST'])
def broker_form():
    # UP : Work on securing this route
    session['is_checked'] = 'c'
    prod = login_model.Broker.query.filter_by(broker_name=request.form['city']).first()
    prod_a = login_model.Broker.query.filter_by(contact=request.form['contact']).first()
    if prod and prod_a :
            mssg = "Duplicate Data "
            return redirect(url_for('basic_master'))
    else:
        query = login_model.City.query.filter_by(id=int(request.form['city'])).first()
        new_data = login_model.Broker(broker_name=request.form['broker_name'].upper() , city = query.city ,
        state = query.state,  country = query.country , contact = request.form['contact'] ) 

        try:
            db.session.add(new_data)
            db.session.commit()
            mssg = "Data Successfully added 👍"
            return redirect(url_for('basic_master'))


        except Exception as e:
            mssg = "Error occured while adding data 😵. Here's the error : "+str(e)
            return redirect(url_for('basic_master'))

################## Delete & Edit Production category Routes ################
#############################################################################


@app.route('/delete/product/<item_id>' , methods=['GET', 'POST'])
@login_required
def delete_data_prod(item_id):
    '''
        Deletes data from the Data Display Table
        Requires Args :
        INPUT : item_id

        ** FIX : Needs refactoring , using a signle routes for delete in multiple tables
        
    '''
    login_model.ProdCat.query.filter_by(id=int(item_id)).delete()
    db.session.commit()
    mssg = "Data Successfully deleted"
    return redirect(url_for('basic_master'))

@app.route('/edit/product/<item_id>' , methods=['GET' , 'POST'])
@login_required
def edit_data_prod(item_id):
    '''
        Edits data from the Data Display Table
        Requires Args :
        INPUT : item_id

        ** FIX : Needs refactoring , using a single routes for delete in multiple tables
        
    '''
    temp = login_model.ProdCat.query.filter_by(id=int(item_id)).first()
    temp.prod_cat = request.form['edit_input'].upper()
    db.session.commit()
    mssg = "Data Successfully Edited" 
    return redirect(url_for('basic_master'))


################## Delete & Edit Comm Channels Routes ################
#############################################################################


@app.route('/delete/comm/<item_id>' , methods=['GET', 'POST'])
@login_required
def delete_data_comm(item_id):
    '''
        Deletes data from the Data Display Table
        Requires Args :
        INPUT : item_id

        ** FIX : Needs refactoring , using a signle routes for delete in multiple tables
        
    '''
    login_model.CommChannel.query.filter_by(id=int(item_id)).delete()
    db.session.commit()
    mssg = "Data Successfully deleted"
    return redirect(url_for('basic_master'))

@app.route('/edit/comm/<item_id>' , methods=['GET' , 'POST'])
@login_required
def edit_data_comm(item_id):
    '''
        Edits data from the Data Display Table
        Requires Args :
        INPUT : item_id

        ** FIX : Needs refactoring , using a single routes for delete in multiple tables
        
    '''
    temp = login_model.CommChannel.query.filter_by(id=int(item_id)).first()
    temp.channel = request.form['edit_input'].upper()
    db.session.commit()
    mssg = "Data Successfully Edited" 
    return redirect(url_for('basic_master'))

################## Delete & Edit Credit Health Routes ################
#############################################################################


@app.route('/delete/health/<item_id>' , methods=['GET', 'POST'])
@login_required
def delete_data_health(item_id):
    '''
        Deletes data from the Data Display Table
        Requires Args :
        INPUT : item_id

        ** FIX : Needs refactoring , using a signle routes for delete in multiple tables
        
    '''
    print
    login_model.HealthCode.query.filter_by(id=int(item_id)).delete()
    db.session.commit()
    mssg = "Data Successfully deleted"
    return redirect(url_for('basic_master'))

@app.route('/edit/health/<item_id>' , methods=['GET' , 'POST'])
@login_required
def edit_data_health(item_id):
    '''
        Edits data from the Data Display Table
        Requires Args :
        INPUT : item_id

        ** FIX : Needs refactoring , using a single routes for delete in multiple tables
        
    '''
    temp = login_model.HealthCode.query.filter_by(id=int(item_id)).first()
    temp.health = request.form['edit_input'].upper()
    db.session.commit()
    mssg = "Data Successfully Edited" 
    return redirect(url_for('basic_master'))

################## Delete & Edit Bussniess Category Routes ################
#############################################################################


@app.route('/delete/buss/<item_id>' , methods=['GET', 'POST'])
@login_required
def delete_data_buss(item_id):
    '''
        Deletes data from the Data Display Table
        Requires Args :
        INPUT : item_id

        ** FIX : Needs refactoring , using a signle routes for delete in multiple tables
        
    '''
    print
    login_model.BussCat.query.filter_by(id=int(item_id)).delete()
    db.session.commit()
    mssg = "Data Successfully deleted"
    return redirect(url_for('basic_master'))

@app.route('/edit/buss/<item_id>' , methods=['GET' , 'POST'])
@login_required
def edit_data_buss(item_id):
    '''
        Edits data from the Data Display Table
        Requires Args :
        INPUT : item_id

        ** FIX : Needs refactoring , using a single routes for delete in multiple tables
        
    '''
    temp = login_model.BussCat.query.filter_by(id=int(item_id)).first()
    temp.buss_cat = request.form['edit_input'].upper()
    db.session.commit()
    mssg = "Data Successfully Edited" 
    return redirect(url_for('basic_master'))

################## Delete & Edit State Routes ################
#############################################################################


@app.route('/delete/state/<item_id>' , methods=['GET', 'POST'])
@login_required
def delete_data_state(item_id):
    '''
        Deletes data from the Data Display Table
        Requires Args :
        INPUT : item_id

        ** FIX : Needs refactoring , using a signle routes for delete in multiple tables
        
    '''
    print
    login_model.State.query.filter_by(id=int(item_id)).delete()
    db.session.commit()
    mssg = "Data Successfully deleted"
    return redirect(url_for('basic_master'))

@app.route('/edit/state/<item_id>' , methods=['GET' , 'POST'])
@login_required
def edit_data_state(item_id):
    '''
        Edits data from the Data Display Table
        Requires Args :
        INPUT : item_id

        ** FIX : Needs refactoring , using a single routes for delete in multiple tables
        
    '''
    temp = login_model.State.query.filter_by(id=int(item_id)).first()
    temp.state = request.form['edit_input'].upper()
    db.session.commit()
    mssg = "Data Successfully Edited" 
    return redirect(url_for('basic_master'))


################## Delete & Edit Country Routes ################
#############################################################################


@app.route('/delete/country/<item_id>' , methods=['GET', 'POST'])
@login_required
def delete_data_country(item_id):
    '''
        Deletes data from the Data Display Table
        Requires Args :
        INPUT : item_id

        ** FIX : Needs refactoring , using a signle routes for delete in multiple tables
        
    '''
    print
    login_model.Country.query.filter_by(id=int(item_id)).delete()
    db.session.commit()
    mssg = "Data Successfully deleted"
    return redirect(url_for('basic_master'))

@app.route('/edit/country/<item_id>' , methods=['GET' , 'POST'])
@login_required
def edit_data_country(item_id):
    '''
        Edits data from the Data Display Table
        Requires Args :
        INPUT : item_id

        ** FIX : Needs refactoring , using a single routes for delete in multiple tables
        
    '''
    temp = login_model.Country.query.filter_by(id=int(item_id)).first()
    temp.country = request.form['edit_input'].upper()
    db.session.commit()
    mssg = "Data Successfully Edited" 
    return redirect(url_for('basic_master'))

################## Delete & Edit City Routes ################
#############################################################################


@app.route('/delete/city/<item_id>' , methods=['GET', 'POST'])
@login_required
def delete_data_city(item_id):
    '''
        Deletes data from the Data Display Table
        Requires Args :
        INPUT : item_id

        ** FIX : Needs refactoring , using a signle routes for delete in multiple tables
        
    '''
    print
    login_model.City.query.filter_by(id=int(item_id)).delete()
    db.session.commit()
    mssg = "Data Successfully deleted"
    return redirect(url_for('basic_master'))

@app.route('/edit/city/<item_id>' , methods=['GET' , 'POST'])
@login_required
def edit_data_city(item_id):
    '''
        Edits data from the Data Display Table
        Requires Args :
        INPUT : item_id

        ** FIX : Needs refactoring , using a single routes for delete in multiple tables
        
    '''
    temp = login_model.City.query.filter_by(id=int(item_id)).first()
    temp.city = request.form['edit_input'].upper()
    db.session.commit()
    mssg = "Data Successfully Edited" 
    return redirect(url_for('basic_master'))

################## Delete & Edit Broker Routes ################
#############################################################################


@app.route('/delete/broker/<item_id>' , methods=['GET', 'POST'])
@login_required
def delete_data_broker(item_id):
    '''
        Deletes data from the Data Display Table
        Requires Args :
        INPUT : item_id

        ** FIX : Needs refactoring , using a signle routes for delete in multiple tables
        
    '''
    print
    login_model.Broker.query.filter_by(id=int(item_id)).delete()
    db.session.commit()
    mssg = "Data Successfully deleted"
    return redirect(url_for('basic_master'))

@app.route('/edit/broker/<item_id>' , methods=['GET' , 'POST'])
@login_required
def edit_data_broker(item_id):
    '''
        Edits data from the Data Display Table
        Requires Args :
        INPUT : item_id

        ** FIX : Needs refactoring , using a single routes for delete in multiple tables
        
    '''
    temp = login_model.Broker.query.filter_by(id=int(item_id)).first()
    temp.broker_name = request.form['edit_input'].upper()
    db.session.commit()
    mssg = "Data Successfully Edited" 
    return redirect(url_for('basic_master'))




@app.route('/user_profile' , methods=['GET' , 'POST'])
@login_required
def user_profile():
    '''
        Basic master setup done here
    '''
    pass
