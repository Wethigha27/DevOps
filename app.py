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


@app.route('/interventions')
def liste_interventions():
    if 'util' not in session:
        session.clear()
        return redirect(url_for('auth'))
    interventions = Intervention.query.all()  # Fetch all interventions
    for intervention in interventions:
        # Fetch the corresponding client and intervenant
        client = Client.query.get(intervention.IdClient)
        intervenant = Intervenant.query.get(intervention.IdIntervenants)
        
        # Assign the prenoms to intervention attributes
        intervention.client_prenom = client.Prenom if client else "N/A"
        intervention.intervenant_prenom = intervenant.Prenom if intervenant else "N/A"

    return render_template('liste_interventions.html', interventions=interventions)

    
# from flask import jsonify

@app.route('/ajouter_intervention', methods=['GET', 'POST'])
def ajouter_intervention():
    if request.method == 'POST':
        # Retrieve the form data
        # print("_/chhhhh")
        
        # Récupérer les données du formulaire
        date = request.form.get('date')
        intervenant_id = request.form.get('idIntervenants')
        client_id = request.form.get('idClient')
        motive = request.form.get('motive')
        etat = request.form.get('etat')
        type = request.form.get('type')

        # Validation for required fields
        if not date or not intervenant_id or not client_id:
            flash("Tous les champs sont requis.", "error")
            return redirect(url_for('ajouter_intervention'))

        # Convert date and ids
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            intervenant_id = int(intervenant_id)
            client_id = int(client_id)
        except ValueError as e:
            flash("Format de date ou d'ID invalide.", "error")
            return redirect(url_for('ajouter_intervention'))

        # Create the new intervention
        nouvelle_intervention = Intervention(
            Date=date_obj,
            IdIntervenants=intervenant_id,
            IdClient=client_id,
            Etat=etat,
            Motive=motive,
            Type=type
        )

        # Save to the database
        try:
            db.session.add(nouvelle_intervention)
            db.session.commit()
            return {'status': 'success', 'message': 'L/intervention a été supprimé avec succès!'} 
            # return redirect(url_for('liste_interventions'))
        except Exception as e:
            db.session.rollback()
            flash("Une erreur s'est produite lors de l'ajout de l'intervention.", "error")

    # Fetch clients and intervenants from the database
    clients = Client.query.all()
    intervenants = Intervenant.query.all()
    print("/__ch")

    return render_template('liste_interventions.html', clients=clients, intervenants=intervenants)



@app.route('/get_clients_intervenants', methods=['GET'])
def get_clients_intervenants():
    # Récupération des intervenants et des clients pour les afficher dans les listes déroulantes
    intervenants = Intervenant.query.all()
    clients = Client.query.all()

    # Structure des données pour la réponse JSON
    data = {
        'clients': [{'id': client.IdClient, 'prenom': client.Prenom, 'nom': client.Nom} for client in clients],
        'intervenants': [{'id': intervenant.IdIntervenant, 'prenom': intervenant.Prenom, 'nom': intervenant.Nom} for intervenant in intervenants]
    }
    
    return jsonify(data)
from flask import make_response

@app.route('/modifier_intervention/<int:id>', methods=['GET', 'POST'])
def modifier_intervention(id):
    intervention = Intervention.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # Update the intervention fields with the new data from the form
            intervention.Type = request.form.get('type')
            intervention.Motive = request.form.get('motive')
            intervention.Etat = request.form.get('etat')

            # Commit the changes
            db.session.commit()
            
            return {'status': 'success', 'message': 'L\'intervention a été modifiée avec succès!'}

        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            return {'status': 'error', 'message': 'Une erreur est survenue lors de la modification.'}

    response = make_response(render_template('modifier_intervention.html', intervention=intervention))
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.route('/supprimer_intervention/<int:id>', methods=['POST'])
def supprimer_intervention(id):
    intervention = Intervention.query.get_or_404(id)
    try:
        db.session.delete(intervention)
        db.session.commit()
        return {'status': 'success', 'message': 'L\'intervention a été supprimée avec succès!'}
    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
    return {'status': 'error', 'message': 'Une erreur est survenue lors de la suppression.'}

# @app.route('/chi')
# def afficher_formulaire():
#     clients = Client.query.all()
#     intervenants = Intervenant.query.all()
#     return render_template('test.html', clients=clients, intervenants=intervenants)

