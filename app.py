# importation des bibliothèques et des fonctions nécessaires
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split 
import piskle
import email
from flask import Flask, request, jsonify, render_template

app = Flask(__name__) # initialisation de l'application flask
model = piskle.load('model.pskl') # chargement du modèle
emails = pd.read_csv('email_dataset.csv', keep_default_na=False) # dataframe utilisé pour la modélisation
df = pd.read_csv('giskard_dataset.csv', sep=';', index_col=[0]) # dataframe utilisé pour l'affichage de l'email original
df = df.reset_index().drop(axis=1, columns = 'index') # évite les erreurs de corruption (utilisé dans le notebook original)


# définition des données compréhensibles par le modèle
X = emails.drop('Target', axis=1)
y = emails['Target']

# split des données
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.10, random_state=933) 


@app.route('/') # page d'accueil
def home():
    menu = list(range(0, len(x_test)))
    return render_template('index.html', menu=menu)

@app.route('/estimation',methods=['POST', 'GET'])
def estimation():
    '''
    Pour visualiser les résultats sur l'interface graphique HTML
    '''
    
    # menu de sélection
    menu = list(range(0, len(x_test))) # menu de sélection
    x = int(request.form.get("menu")) # valeur du menu choisie
    
    # comparaison estimation - réel
    estimation = model.predict(x_test)[x] # estimation pour la valeur choisie
    real = y_test.iloc[x] # valeur réelle
    

    # email sélectionné    
    index_list = x_test.index.tolist() # pour correspondre le dataset original (df) et celui de test (emails)
    #raw_email = df.loc[index_list[x]]['Message']
    
    # preprocessing de l'email pour en extraire les infos voulues (subject, from, to, date, body)   
    def preproc(x):
        msg = df.loc[index_list[x]]['Message']
        email_message = email.message_from_string(msg)
        for part in email_message.walk(): 
            if part.get_content_type()=="text/plain" or part.get_content_type()=="text/html":
                message = part.get_payload(decode=True)
                a = "Subject: "
                a_content = email_message["subject"]
                b = "\n\n From: "
                b_content = email_message["from"]
                c = "\n To:"
                c_content = email_message["to"]
                d = "\n Date: "
                d_content = email_message["date"]
                e = "\n\n  Message: \n"
                e_content = message.decode()
                list_email = [a, a_content, b, b_content, c, c_content, d, d_content, e, e_content]
                pre_email = ''.join(filter(None, list_email)) # filtre les None (sinon erreur)
                
                return pre_email
            
    raw_email = preproc(x)
        
    # affichage
    return render_template('index.html', menu=menu, estimated_class='''Thème d'email estimé: {}'''.format(estimation), real_class='''(Thème d'email réel: {})'''.format(real), raw_email=raw_email)

if __name__ == "__main__":
    app.run(host='0.0.0.0')

