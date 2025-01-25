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
