from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO
import os
import pandas as pd
import json

import pymysql.cursors

from models.user import User
from models.modeluser import ModelUser


# Creacion del servidor
app = Flask(__name__)
socketio= SocketIO(app)

## Clase - Base de datos
db = ModelUser()

## Clave secreta de session
app.secret_key = 'B!1W8NAt1T^%KVHUI*S^'


login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return db.get_by_id(id)


## Rutas raiz del servidor
@app.route('/')
def home():
    return render_template('admin.html')


## Ruta login
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        user =  User(0, request.form['username'], request.form['password'])
        logged_user = db.login(user)

        if logged_user != None and logged_user.password == True: # Probar combinar declaraciones
            login_user(logged_user)

            if logged_user.role == 'admin':
                return redirect(url_for('admin_page'))
            else: 
                return redirect(url_for('user_page'))
        else:
            flash("Usuario y/o contraseña invalida...")
            return render_template('login.html')
    else:
        return render_template('login.html')


## Ruta de admin
@app.route('/admin')
@login_required
def admin_page():
    return render_template('admin.html')


## Ruta de usuario
@app.route('/user')
@login_required
def user_page():
    opcion = db.get_clients()
    return render_template('user.html', categoria = opcion)

def notify_new_message():
    socketio.emit('new_message', get_data_table())



## Ruta de webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():  
    if request.method == 'POST':
        data = request.json
        try:
            db.insert_db(data['query'])
            notify_new_message()

            return jsonify({'status': 'success'}), 200
        except Exception as ex:
            # return jsonify({'status': 'Failed'}), 400
            raise Exception(ex)


## Ruta para actualizar la tabla GET - get_data_table
@app.route('/get_data_table', methods=['POST'])
def get_data_table():
    # info = request.json
    data = db.prueba_filtros(request.get_json())
    return jsonify(data)


@app.route('/get_client_table', methods=['GET'])
def get_client_table():
    data = db.get_client_table()
    return jsonify(data)

@app.route('/filter_content', methods=['POST'])
def filter_content():
    print(request.get_json())
    return jsonify([])

## Ruta para cargar tabla
@app.route('/cargar_datos', methods=['POST'])
def cargar_datos():
    ## Inserta para notificar que el numero ya esta registrado
    
    data = request.form
    try:
        db.insert_client(data)
        return redirect(url_for('admin_page'))
    except Exception as ex:
        raise Exception(ex)


@app.route('/modify_data/<int:id>', methods=['POST'])
def modify_data(id):
    try:
        db.update_data(id)
        return jsonify({"success": True, "message": "Mensaje modificado correctamente"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# @app.route('/filter_content', methods=[])

## Log out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True, port=5000)