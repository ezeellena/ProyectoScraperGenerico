import os

import requests
from werkzeug.utils import secure_filename
from wordpress_xmlrpc import Client, WordPressPost, xmlrpc_client
from wordpress_xmlrpc.methods import posts, media
import json
from flask import Flask, request
import requests
import mysql.connector
from bs4 import BeautifulSoup
from tldextract import tldextract
import urllib.request
import pyodbc
"""
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'Server=localhost;'
                      'Database=ScraperNoticias;'
                      'Trusted_Connection=yes;')
"""
conn = mysql.connector.connect(
  host="167.86.120.98",
  port="3307",
  database="test_portales",
  user="root",
  password="dalas.2009"
)

if __name__ == "__main__":

    sql = "SELECT link FROM todas_las_noticias where medio in (select link from portales_wordpress) and link not in (select link from noticias_basura) and link not in (select link from noticias_enviadas_wordpress)"
    mycursor = conn.cursor()
    mycursor.execute(sql)
    Portales = mycursor.fetchall()
    for link in Portales:

        response2 = requests.get(link[0]).text
        j = open("configParaWordpress.json", "r")
        confiTagPage = {}
        confiTagPage = json.loads(j.read())

        nueva_entrada = WordPressPost()
        for Noti in confiTagPage["j"]["imagenNoticia"]:
            try:
                imagen = eval(Noti)
                if imagen != []:
                    try:
                        nueva_entrada.thumbnail = imagen
                    except Exception as e:
                        print(e)
            except Exception as e:
                print("Error al Obtener Articulos de noticias ", e)

        urllib.request.urlretrieve(imagen, "./img" + "local-filename.jpg")
        # filename = secure_filename(f)
        # f.save(os.path.join('./img', filename))
        # filename = '/path/to/my/picture.jpg'
        data = {
            'name': 'picture.jpg',
            'type': 'image/jpeg',  # mimetype
        }

        # read the binary file and let the XMLRPC library encode it into base64
        with open("./img" + "local-filename.jpg", 'rb') as img:
            data['bits'] = xmlrpc_client.Binary(img.read())
        usuario = "Sergio"
        contraseña = "sergio"
        sitio = "https://somoscampoonline.com/xmlrpc.php"
        cliente = Client(sitio, usuario, contraseña)
        response = cliente.call(media.UploadFile(data))
        imagenParaPublicar = response['id']
        nueva_entrada.thumbnail = imagenParaPublicar
        nueva_entrada.post_status = 'publish'

        for Noti in confiTagPage["j"]["tituloNoticia"]:
            try:
                titulo = eval(Noti)
                if titulo != []:
                    try:
                        if len(titulo) > 3:
                            nueva_entrada.title = titulo
                    except Exception as e:
                        print(e)
            except Exception as e:
                print("Error al Obtener Articulos de noticias ", e)


        for Noti in confiTagPage["j"]["descripcionNoticia"]:
            try:
                descripcion = eval(Noti)
                if descripcion != []:
                    try:
                        if len(descripcion) > 5:
                            nueva_entrada.content = descripcion +"\n"+  "Fuente: "+ link[0] +""
                        else:
                            nueva_entrada.content = "Fuente: " + link[0] + ""
                    except Exception as e:
                        print(e)
            except Exception as e:
                print("Error al Obtener Articulos de noticias ", e)

        if not nueva_entrada.content or not nueva_entrada.title or not nueva_entrada.thumbnail:
            break
        #nueva_entrada.title = titulo
        #nueva_entrada.content = texto
        #nueva_entrada.terms_names = {
            #'post_tag': ['AI', 'musk'],
            #'category': ['Technology', 'Chemistry']}
        id_entrada_publicada = cliente.call(posts.NewPost(nueva_entrada))
        mycursor = conn.cursor()
        sql = "INSERT INTO noticias_enviadas_wordpress (link, titulo, descripcion) " \
              "VALUES (%s, %s, %s)"
        val = (link[0], nueva_entrada.title,nueva_entrada.content)
        mycursor.execute(sql, val)
        conn.commit()
        print("Correcto! Se publicó la entrada, y su id es {}".format(id_entrada_publicada))





