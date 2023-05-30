from flask import Flask, redirect, url_for, render_template,Markup,send_file,url_for,request,jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import json
from sqlalchemy import text,column,literal,tuple_
import requests

# -*- coding: utf-8 -*-

app = Flask(__name__, template_folder='template')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True 
db = SQLAlchemy(app)

api = Api(app)


################################################################ Database Table ######################################################################### 
class IngredientModel(db.Model):
    __tablename__ = 'ingredients'
    ing_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    #quantite = db.Column(db.Float)

    #recettes = db.relationship("RecetteModel", secondary='recette_ingredient', back_populates="ingredients")


    def __repr__(self):
        return f"Ingredient('{self.ing_id}', '{self.name}', '{self.description}')"
    
class EpicesModel(db.Model):
    __tablename__ = 'epices'
    epice_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    #quantite = db.Column(db.Float)

    def __repr__(self):
        return f"Epices('{self.epice_id}', '{self.name}', '{self.description}')"

class RecetteModel(db.Model):
    __tablename__ = 'recettes'
    rec_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    categorie = db.Column(db.String(100), nullable=False)
    temps = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    videos = db.Column(db.String(100))
    #ingredient = db.Column(db.String(100))
    

    ingredients = db.relationship('IngredientModel', secondary='recette_ingredient', backref='recettes')
    epices = db.relationship('EpicesModel', secondary='recette_epice', backref='recettes')
    

    def __repr__(self):
        return f"Recette('{self.rec_id}', '{self.name}', '{self.type}', '{self.categorie}', '{self.temps}', '{self.image}', '{self.description}' ,'{self.videos}')"

class RecetteIngredient(db.Model):
    __tablename__ = 'recette_ingredient'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    rec_id = db.Column(db.Integer, db.ForeignKey('recettes.rec_id'))
    ing_id = db.Column(db.Integer, db.ForeignKey('ingredients.ing_id'))
    

class RecetteEpices(db.Model):
    __tablename__ = 'recette_epice'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    rec_id = db.Column(db.Integer, db.ForeignKey('recettes.rec_id'))
    epice_id = db.Column(db.Integer, db.ForeignKey('epices.epice_id'))

class Avis(db.Model):
    __tablename__ = 'avis'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    q1 = db.Column(db.String)
    q2 = db.Column(db.String)
    q3 = db.Column(db.String)
    commentaire = db.Column(db.String)

    def __init__(self, q1, q2, q3, commentaire):
        self.q1 = q1
        self.q2 = q2
        self.q3 = q3
        self.commentaire = commentaire
    




########################################################## view the databse ##########################################
admin = Admin(app, name='Cuisine Admin', template_mode='bootstrap3')
admin.add_view(ModelView(IngredientModel, db.session))
admin.add_view(ModelView(EpicesModel, db.session))
admin.add_view(ModelView(RecetteModel, db.session))
#admin.add_view(ModelView(RecetteIngredient, db.session))
admin.add_view(ModelView(RecetteEpices, db.session))
#admin.add_view(ModelView(Avis, db.session))
#"""
class RecetteIngredientView(ModelView):
    column_list = ('rec_id', 'ing_id')  # Liste des colonnes à afficher dans la vue
    form_columns = ('rec_id', 'ing_id')  # Liste des colonnes à afficher dans le formulaire d'édition
    column_labels = {'rec_id': 'Recette ID', 'ing_id': 'Ingredient ID'}  # Labels personnalisés pour les colonnes

# Ajouter la vue personnalisée à l'interface d'administration
admin.add_view(RecetteIngredientView(RecetteIngredient, db.session))
#"""

class AvisAdminView(ModelView):
    column_list = ['q1', 'q2', 'q3', 'commentaire']
    column_labels = {'q1': 'Q1', 'q2': 'Q2', 'q3': 'Q3', 'commentaire': 'Commentaire'}
    form_columns = ['q1', 'q2', 'q3', 'commentaire']

admin.add_view(AvisAdminView(Avis, db.session))
######################################################### Route ######################################################
@app.route('/')
def home():
    return render_template('index.html')

#categorie navbar 
@app.route('/Categorie', methods=['GET', 'POST'])
def categorie_view():
    valid_cat = ['Marocaine','Italienne', 'Mexicaine','France', 'Americaine','Asiatique','Indien','Greek','Moyen orient']

    if request.method == 'POST':
        selected_cat = request.form['categorie']
        if selected_cat not in valid_cat and selected_cat != 'All':
            return jsonify({'status': 'error', 'message': 'Le type n\'est pas valide'}), 400

        try:
            sql_query = text(f"SELECT name, type, categorie, temps,image FROM recettes WHERE Categorie = '{selected_cat}'")
            result = db.session.execute(sql_query)
            recettes = result.fetchall()
        except Exception as e:
            print("Erreur SQL :", e)
            return jsonify({'status': 'error', 'message': 'Erreur de base de données'}), 500

        recettes_list = [{'name': recette.name, 'type': recette.type, 'categorie': recette.categorie, 'temps': recette.temps,'image':recette.image} for recette in recettes]
        return jsonify({'status': 'success', 'recettes': recettes_list}), 200

    return render_template('categorie.html', valid_cat=valid_cat), 200

#recette ptidej-dej-dess
@app.route('/Types', methods=['GET', 'POST'])
def types_view():
    valid_types = ['Plat principal', 'Dessert', 'Petit dejeuner','Assortissement']

    if request.method == 'POST':
        selected_type = request.form['type']
        if selected_type not in valid_types and selected_type != 'All':
            return jsonify({'status': 'error', 'message': 'Le type n\'est pas valide'}), 400

        try:
            if selected_type == 'All':
                sql_query = text("SELECT name, type, categorie, temps, videos FROM recettes")
            else:
                sql_query = text(f"SELECT name, type, categorie, temps, videos FROM recettes WHERE type = '{selected_type}'")
            result = db.session.execute(sql_query)
            recettes = result.fetchall()
        except Exception as e:
            print("Erreur SQL :", e)
            return jsonify({'status': 'error', 'message': 'Erreur de base de données'}), 500

        recettes_list = [{'name': recette.name, 'type': recette.type, 'categorie': recette.categorie, 'temps': recette.temps, 'videos': recette.videos} for recette in recettes]
        return jsonify({'status': 'success', 'recettes': recettes_list}), 200

    return render_template('types.html', valid_types=valid_types), 200

#choisir les ingredients 
@app.route('/Ingredients', methods=['GET'])
def ingredient_view():
    try:
        descriptions = db.session.query(IngredientModel.description.distinct()).all()
        descriptions = [d[0] for d in descriptions]
        ingredients = db.session.query(IngredientModel).all()
    except Exception as e:
        print("Erreur SQL :", e)
        return jsonify({'status': 'error', 'message': 'Erreur de base de données'}), 500

    return render_template('ingredient.html', descriptions=descriptions, ingredients=ingredients), 200

"""
class RecetteModel(db.Model):
    __tablename__ = 'recettes'
    rec_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    categorie = db.Column(db.String(100), nullable=False)
    temps = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    videos = db.Column(db.String(100))
"""
#resultat de la recette rechercher 




@app.route('/Recette', methods=['GET', 'POST'])
def resultat_view():
    if request.method == 'POST':
        try:
            selected_ingredients = request.form.getlist('ingredient')
            placeholders = ', '.join(':ingredient{}'.format(i) for i in range(len(selected_ingredients)))
            sql_query = text("SELECT r.name, r.type, r.categorie, r.temps, r.image, r.description FROM recettes r JOIN recette_ingredient ri ON r.rec_id = ri.rec_id JOIN ingredients i ON ri.ing_id = i.ing_id WHERE i.name IN ({})".format(placeholders))
            params = {'ingredient{}'.format(i): ingredient for i, ingredient in enumerate(selected_ingredients)}
            result = db.session.execute(sql_query, params)
            matching_recipe = result.fetchone()
            
            """
            placeholders = ', '.join('?' for i in selected_ingredients)
            sql_query = text(f"SELECT r.rec_id, r.name, r.type, r.categorie, r.temps, r.image, r.description FROM Recettes r WHERE r.rec_id IN (SELECT ra.rec_id FROM recette_ingredient ra JOIN ingredients a ON ra.ing_id = a.ing_id WHERE a.name IN ({placeholders})) AND r.rec_id NOT IN (SELECT ra.rec_id FROM recette_ingredient ra JOIN ingredients a ON ra.ing_id = a.ing_id WHERE a.name NOT IN ({placeholders}))")
            params = selected_ingredients + selected_ingredients
            result =db.session.execute(sql_query, params)
            matching_recipe = result.fetchone()"""
        except Exception as e:
            print("Erreur SQL:", e)
            return jsonify({'status': 'error', 'message': 'Erreur de base de données'}), 500

        return render_template('resultat.html', recipe=matching_recipe), 200

    elif request.method == 'GET' and 'name' in request.args:
        get_name = request.args.get('name')
        sql_query = text("SELECT name, type, categorie, temps, image, description FROM recettes WHERE name = :name")
        result = db.session.execute(sql_query, {'name': get_name})
        matching_recipe = result.fetchone()

        if matching_recipe is None:
            return jsonify({'status': 'error', 'message': 'Recette introuvable'}), 404

        return render_template('resultat.html', recipe=matching_recipe), 200

    else:
        return jsonify({'status': 'error', 'message': 'Erreur de base de données'}), 500

#Avis a l'utilisateur dedicasse Caroline 
@app.route('/Avis', methods=['GET', 'POST'])
def avis_view():
    if request.method == 'POST':
        data = request.get_json()
        q1 = data['q1']
        q2 = ', '.join(data['q2'])
        q3 = data['q3']
        commentaire = data['commentaire']

        # Enregistrer l'avis dans la base de données
        avis = Avis(q1=q1, q2=q2, q3=q3, commentaire=commentaire)
        db.session.add(avis)
        db.session.commit()

        response = {'message': 'Avis enregistré avec succès'}
        return jsonify(response)

    return render_template('avis.html')



######################################################### Main ############################################################
if __name__ == '__main__':
    with app.app_context():
        """
        db.session.query(IngredientModel).delete()
        db.session.query(EpicesModel).delete()
        db.session.query(RecetteModel).delete()
        db.session.commit()
        """
        
        #"""
        db.create_all()


        # Check if the database is already full to not have a duplicate elements in it
        if not IngredientModel.query.first():
            # read and load ingredients from JSON file
            with open('ingredients.json', 'r') as f:
                ingredients_data = json.load(f)

                for ingredient in ingredients_data['ingredients']:
                    ing_id = ingredient['id']
                    name = ingredient['name']
                    description = ingredient['description']
                    new_ingredient = IngredientModel(ing_id=ing_id,name=name, description=description)
                    #new_recette.ingredients.append(RecetteIngredient(rec_id=, ing_id=))
                    db.session.add(new_ingredient)
                    db.session.commit()
        
        if not EpicesModel.query.first():
            # read and load epices from JSON file
            with open('epices.json', 'r') as f:
                epices_data = json.load(f)
                
                for epice in epices_data['epices']:
                    ing_id = epice['id']
                    name = epice['name']
                    description = epice['description']
                    new_epice = EpicesModel(name=name, description=description)
                    #new_recette.epices.append(RecetteEpices(rec_id=, epice_id=))
                    
                    db.session.add(new_epice)
                    db.session.commit() 
        
        if not RecetteModel.query.first():
            # read and load recettes from JSON file
            with open('recettes.json', 'r') as f:
                recettes_data = json.load(f)
                
                for recette in recettes_data['recettes']:
                    rec_id = recette['id']
                    name = recette['name']
                    type = recette['type']
                    categorie = recette['categorie']
                    temps = recette['temps']
                    description = recette['description']
                    image = recette['image']
                    videos = recette['video']
                    # create new recette
                    new_recette = RecetteModel(rec_id=rec_id,name=name, type=type, categorie=categorie, temps=temps, image=image,description=description, videos=videos)
                    db.session.add(new_recette)
                    db.session.commit() 

                    for ingredient_name in recette['ingredient']:
                        ingredient = IngredientModel.query.filter_by(name=ingredient_name).first()
                        if ingredient:
                            relation = RecetteIngredient(rec_id=new_recette.rec_id, ing_id=ingredient.ing_id)
                            db.session.add(relation)
                            db.session.commit()
                    

                #"""

    app.run(debug=True)
