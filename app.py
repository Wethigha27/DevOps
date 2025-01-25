from flask import Flask, render_template, request, redirect, url_for, flash, session,make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import jsonify
import pdfkit
import io
import matplotlib.pyplot as plt
import base64

app=Flask(__name__)
app.secret_key = 'chiva'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bd.sqlite3'
db=SQLAlchemy(app)

class Intervenant(db.Model):
    IdIntervenant=db.Column(db.Integer,primary_key=True)
    Nom=db.Column(db.String(30),nullable=False)
    Prenom=db.Column(db.String(30),nullable=False)
    Post=db.Column(db.String(30),nullable=False)
    interventions = db.relationship('Intervention', backref='intervenant', lazy=True, cascade='all, delete-orphan')

class Client(db.Model):
    IdClient=db.Column(db.Integer,primary_key=True)
    Nom = db.Column(db.String(30),nullable=False)
    Prenom = db.Column(db.String(30),nullable=False)
    Direction=db.Column(db.String(10),nullable=False)
interventions = db.relationship('Intervention', backref='client', lazy=True, cascade='all, delete-orphan')

class Intervention(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Date = db.Column(db.Date, default=datetime.utcnow)
    Type = db.Column(db.String(30), nullable=False)  
    Motive = db.Column(db.String(30), nullable=False)  
    Etat = db.Column(db.String(30), nullable=False)  
    IdIntervenants = db.Column(db.Integer, db.ForeignKey('intervenant.IdIntervenant', ondelete='CASCADE'), nullable=True)
    IdClient = db.Column(db.Integer, db.ForeignKey('client.IdClient', ondelete='CASCADE'))

@app.route('/')
def auth():
    return render_template('authentification.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == "admin" and password == "1234":
        session['util'] = 'admin'
        return redirect(url_for('navbar'))
    else:
        return render_template('authentification.html', error="Nom d'utilisateur ou mot de passe incorrect.")

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/logout',methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('auth'))

@app.route('/navbar')
def navbar():
    if 'util' not in session:
        session.clear()
        return redirect(url_for('auth'))
    return render_template('navbar.html') 

@app.route('/intervenants')
def liste_intervenants():
    if 'util' not in session:
        session.clear()
        return redirect(url_for('auth'))
    else:
        intervenants = Intervenant.query.all()
        return render_template('liste_intervenants.html', intervenants=intervenants)

@app.route('/ajouter_intervenant', methods=['POST'])
def ajouter_intervenant():
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    post = request.form.get('post')

    print(f"Received data - Nom: {nom}, Prenom: {prenom}, Poste: {post}")  # Debug log

    try:
        nouvel_intervenant = Intervenant(Nom=nom, Prenom=prenom, Post=post)
        db.session.add(nouvel_intervenant)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Intervenant ajouté avec succès!'})
    except Exception as e:
        print(f"Error occurred: {e}")  # Debug log
        return jsonify({'status': 'error', 'message': f'Erreur lors de l\'ajout: {str(e)}'})
 # return render_template('ajouter_intervenant.html')

@app.route('/modifier_intervenant/<int:id>', methods=['GET', 'POST'])
def modifier_intervenant(id):
    intervenant = Intervenant.query.get_or_404(id)
    try:
        intervenant.Nom = request.form.get('nom')
        intervenant.Prenom = request.form.get('prenom')
        intervenant.Post = request.form.get('post')
        
        db.session.commit()
        return {'status': 'success', 'message': 'L\'intervenant a été modifiée avec succès!'}
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")  # Optionally log the error for debugging
            
            # Return error response
        return {'status': 'error', 'message': 'Une erreur est survenue lors de la modification.'}

@app.route('/supprimer_intervenant/<int:id>', methods=['POST'])
def supprimer_intervenant(id):
    intervenant = Intervenant.query.get_or_404(id)
    try:
        db.session.delete(intervenant)
        db.session.commit()
        return {'status': 'success', 'message': 'L\'intervenant a été supprimée avec succès!'}
    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
    return {'status': 'error', 'message': 'Une erreur est survenue lors de la suppression.'}

@app.route('/clients')
def liste_clients():
    if 'util' not in session:
        session.clear()
        return redirect(url_for('auth'))
    clients = Client.query.all()
    return render_template('liste_clients.html', clients=clients)


from flask import jsonify

@app.route('/ajouter_client', methods=['GET', 'POST'])
def ajouter_client():
    if request.method == 'POST':
        # Get client details from the form
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        direction = request.form.get('direction')
        
        # Create a new Client object
        nouveau_client = Client(Nom=nom, Prenom=prenom, Direction=direction)
        
        # Add the client to the database
        db.session.add(nouveau_client)
        db.session.commit()
        
        # Return a JSON response indicating success
        return jsonify({
            'status': 'success',
            'message': 'Client ajouté avec succès!'
        })
    
    # Handle GET request if necessary, e.g., rendering the form
    # return render_template('ajouter_client.html')

    # return render_template('ajouter_client.html')

@app.route('/modifier_client/<int:id>', methods=['GET', 'POST'])
def modifier_client(id):
    client = Client.query.get_or_404(id)
    try:
        client.Nom = request.form.get('nom')
        client.Prenom = request.form.get('prenom')
        client.Direction = request.form.get('direction')
        
        db.session.commit()
        return {'status': 'success', 'message': 'Le client a été modifié avec succès!'}
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")  # Optionally log the error for debugging
        return {'status': 'error', 'message': 'Une erreur est survenue lors de la modification.'}


  
# return redirect(url_for('liste_interventions'))

@app.route('/supprimer_client/<int:id>', methods=['POST'])
def supprimer_client(id): 
    client = Client.query.get_or_404(id) 
    try: 
        db.session.delete(client) 
        db.session.commit() 
        return {'status': 'success', 'message': 'Le client a été supprimé avec succès!'} 
    except Exception as e: 
        db.session.rollback()  # Rollback in case of an error 
        print(f"Error: {e}")  
    return {'status': 'error', 'message': 'Une erreur est survenue lors de la suppression.'}
