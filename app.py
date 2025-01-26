from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps  
from flask import send_file
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from functools import wraps 
import json
import plotly 
import plotly.express as px
import plotly.graph_objects as go
import json
from flask import jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interventions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'votre_cle_secrete_pour_flash'  
db = SQLAlchemy(app)

class Intervenant(db.Model):
    __tablename__ = 'intervenants'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    poste = db.Column(db.String(100), nullable=False)
    interventions = db.relationship('Intervention', backref='intervenant', cascade="all, delete-orphan", passive_deletes=True)

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    direction = db.Column(db.String(100), nullable=False)
    interventions = db.relationship('Intervention', backref='client', cascade="all, delete-orphan", passive_deletes=True)

class Intervention(db.Model):
    __tablename__ = 'interventions'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    type_intervention = db.Column(db.String(20), nullable=False)
    motif = db.Column(db.String(255), nullable=False)
    etat = db.Column(db.String(20), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)  # Correction ici
    intervenant_id = db.Column(db.Integer, db.ForeignKey('intervenants.id', ondelete='CASCADE'), nullable=True)


# Créer la base de données et les tables au premier lancement
with app.app_context():
    db.create_all()

# Page de connexion
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == "admin" and password == "1234":
            session['logged_in'] = True  # Définir la session comme connectée
            return redirect(url_for('client'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect !", "error")
            return redirect(url_for('login'))

    return render_template('login.html')


# Ajouter une route pour la déconnexion
@app.route('/logout')
def logout():
    session.clear()  # Nettoie toute la session
    return redirect(url_for('login'))


# Empêche le cache des pages pour éviter l'accès après déconnexion
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Vos routes `client`, `add_client`, `edit_client`, etc. vont ici, sans changement.


# Page de gestion des clients
@app.route('/client', methods=['GET', 'POST'])
@login_required
def client():
    if request.method == 'POST':
        # Ajout d'un nouveau client
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        direction = request.form.get('direction')
        
        nouveau_client = Client(nom=nom, prenom=prenom, direction=direction)
        db.session.add(nouveau_client)
        db.session.commit()
        return redirect(url_for('client'))

    # search = request.args.get('search', '').strip()  

    # if search:
    #     clients = Client.query.filter(
    #         (Client.nom.ilike(f'%{search}%')) |
    #         (Client.prenom.ilike(f'%{search}%')) |
    #         (Client.direction.ilike(f'%{search}%'))
    #     ).all()
    # else:
    clients = Client.query.all()

    return render_template('client.html', clients=clients)

@app.route('/client/add', methods=['GET', 'POST'])
@login_required
def add_client():
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        direction = request.form.get('direction')
        
        nouveau_client = Client(nom=nom, prenom=prenom, direction=direction)
        db.session.add(nouveau_client)
        db.session.commit()
        return redirect(url_for('client'))

    return render_template('add_client.html')

@app.route('/client/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_client(id):
    client = Client.query.get_or_404(id)
    if request.method == 'POST':
        client.nom = request.form.get('nom')
        client.prenom = request.form.get('prenom')
        client.direction = request.form.get('direction')
        
        db.session.commit()
        return redirect(url_for('client'))

    return render_template('edit_client.html', client=client)



@app.route('/client/delete/<int:id>', methods=['POST'])
@login_required
def delete_client(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('client'))



@app.route('/intervenants', methods=['GET', 'POST'])
@login_required
def intervenants():
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        poste = request.form.get('poste')
        
        nouvel_intervenant = Intervenant(nom=nom, prenom=prenom, poste=poste)
        db.session.add(nouvel_intervenant)
        db.session.commit()
        return redirect(url_for('intervenants'))

    intervenants = Intervenant.query.all()
    print("Intervenants récupérés :", intervenants)  
    return render_template('intervenants.html', intervenants=intervenants)



@app.route('/intervenants/add', methods=['GET', 'POST'])
@login_required
def add_intervenant():
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        poste = request.form.get('poste')
        
        nouvel_intervenant = Intervenant(nom=nom, prenom=prenom, poste=poste)
        db.session.add(nouvel_intervenant)
        db.session.commit()
        return redirect(url_for('intervenants'))

   
    return render_template('add_intervenant.html')

# Modifier un intervenant
@app.route('/intervenants/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_intervenant(id):
    intervenant = Intervenant.query.get_or_404(id)
    if request.method == 'POST':
        intervenant.nom = request.form.get('nom')
        intervenant.prenom = request.form.get('prenom')
        intervenant.poste = request.form.get('poste')
        db.session.commit()
        return redirect(url_for('intervenants'))

    return render_template('edit_intervenant.html', intervenant=intervenant)

# Supprimer un intervenant
@app.route('/intervenants/delete/<int:id>', methods=['POST'])
@login_required
def delete_intervenant(id):
    intervenant = Intervenant.query.get_or_404(id)
    db.session.delete(intervenant)
    db.session.commit()
    return redirect(url_for('intervenants'))




# Page de gestion des interventions
@app.route('/interventions', methods=['GET', 'POST'])
@login_required
def interventions():
    if request.method == 'POST':
        date = request.form.get('date')
        type_intervention = request.form.get('type_intervention')
        motif = request.form.get('motif')
        etat = request.form.get('etat')
        client_id = request.form.get('client_id')
        intervenant_id = request.form.get('intervenant_id')
        
        # Créer une nouvelle intervention
        nouvelle_intervention = Intervention(
            date=datetime.strptime(date, '%Y-%m-%d'),
            type_intervention=type_intervention,
            motif=motif,
            etat=etat,
            client_id=client_id,
            intervenant_id=intervenant_id
        )
        db.session.add(nouvelle_intervention)
        db.session.commit()
        flash("Intervention ajoutée avec succès !", "success")
        return redirect(url_for('interventions'))

    # Récupérer toutes les interventions pour les afficher
    interventions = Intervention.query.all()
    clients = Client.query.all()
    intervenants = Intervenant.query.all()
    return render_template('interventions.html', interventions=interventions, clients=clients, intervenants=intervenants)

# Page d'ajout d'une intervention
@app.route('/add_intervention', methods=['GET', 'POST'])
@login_required
def add_intervention():
    if request.method == 'POST':
        try:
            date = request.form.get('date')
            type_intervention = request.form.get('type_intervention')
            motif = request.form.get('motif')
            etat = request.form.get('etat')
            client_id = request.form.get('client_id')
            intervenant_id = request.form.get('intervenant_id')

            # Convertir la date
            date_intervention = datetime.strptime(date, '%Y-%m-%d')

            # Création de l'instance d'intervention
            intervention = Intervention(
                date=date_intervention,
                type_intervention=type_intervention,
                motif=motif,
                etat=etat,
                client_id=client_id,
                intervenant_id=intervenant_id
            )

            db.session.add(intervention)
            db.session.commit()
            return redirect(url_for('interventions'))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout de l'intervention : {str(e)}", "error")

    # Si GET, récupérer les clients et intervenants pour le formulaire
    clients = Client.query.all()
    intervenants = Intervenant.query.all()
    return render_template('ajouter_intervention.html', clients=clients, intervenants=intervenants)



# Modifier une intervention
@app.route('/interventions/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_intervention(id):
    intervention = Intervention.query.get_or_404(id)
    clients = Client.query.all()
    intervenants = Intervenant.query.all()
    
    if request.method == 'POST':
        intervention.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        intervention.type_intervention = request.form.get('type_intervention')
        intervention.motif = request.form.get('motif')
        intervention.etat = request.form.get('etat')
        intervention.client_id = request.form.get('client_id')
        intervention.intervenant_id = request.form.get('intervenant_id')
        
        db.session.commit()
        return redirect(url_for('interventions'))

    return render_template('edit_intervention.html', intervention=intervention, clients=clients, intervenants=intervenants)

# Supprimer une intervention
@app.route('/interventions/delete/<int:id>', methods=['POST'])
@login_required
def delete_intervention(id):
    intervention = Intervention.query.get_or_404(id)
    db.session.delete(intervention)
    db.session.commit()
    return redirect(url_for('interventions'))



@app.route('/graphs')
@login_required
def graphs():
    # Récupérer les données des interventions
    interventions = Intervention.query.all()

    # Compter les tâches réalisées et en attente
    total_realisees = sum(1 for intervention in interventions if intervention.etat.lower() == "réalisée")
    total_en_attente = sum(1 for intervention in interventions if intervention.etat.lower() == "en attente")
    
    # Données pour le graphique en secteurs des tâches réalisées/en attente
    data_etat = {
        'État': ['Réalisées', 'En attente'],
        'Nombre': [total_realisees, total_en_attente]
    }
    
    fig_etat = px.pie(data_etat, names='État', values='Nombre', color_discrete_sequence=px.colors.sequential.RdBu)

    # Styliser le titre du graphique des états
    fig_etat.update_layout(
        title={
            'text': "Pourcentage des tâches réalisées et en attente",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'family': 'Arial, sans-serif',
                'size': 18,
                'color': '#343a40',
            },
            'pad': {'b': 20}
        }
    )

    # Ajouter le titre au graphique des tâches réalisées/en attente
    fig_etat.update_layout(
        title={
            'text': "Pourcentage des tâches réalisées et en attente",
            'font': {'size': 24},  # Même taille que pour fig_intervenants
            'x': 0.5,  # Centrer le titre
            'xanchor': 'center'
        }
    )

    # Calculer le pourcentage des tâches réalisées par chaque intervenant
    intervenants = Intervenant.query.all()
    interventions_par_intervenant = []

    for intervenant in intervenants:
        total_taches = len(intervenant.interventions)
        if total_taches > 0:
            total_taches_realisees = sum(1 for intervention in intervenant.interventions if intervention.etat.lower() == "réalisée")
            interventions_par_intervenant.append({
                'Intervenant': f"{intervenant.nom} {intervenant.prenom}",
                'Réalisées': total_taches_realisees,
                'Total': total_taches
            })

    labels = [item['Intervenant'] for item in interventions_par_intervenant]
    values = [item['Réalisées'] for item in interventions_par_intervenant]

    # Ajouter le graphique des tâches réalisées par intervenant avec des couleurs plus agréables
    fig_intervenants = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                marker=dict(
                    colors=px.colors.qualitative.Pastel  # Palette pastel
                )
            )
        ]
    )

    # Ajouter le titre et l'alignement
    fig_intervenants.update_layout(
        title={
            'text': "Pourcentage des tâches réalisées par intervenant",
            'font': {'size': 24},  # Même taille que l'autre graphique
            'x': 0.5,  # Centrer le titre
            'xanchor': 'center'
        }
    )

    # Convertir les figures en JSON pour le rendu avec Plotly.js
    graph_etat = json.dumps(fig_etat, cls=plotly.utils.PlotlyJSONEncoder)
    graph_intervenants = json.dumps(fig_intervenants, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('graphs.html', graph_etat=graph_etat, graph_intervenants=graph_intervenants)


# Exécution de l'application
if __name__ == '__main__':
    app.run(debug=True)


