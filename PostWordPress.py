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

    sql = "SElECT id_padre as idpadre FROM publicador group by id_padre"
    mycursor = conn.cursor()
    mycursor.execute(sql)
    PublicadoresAgrupados = mycursor.fetchall()

    for publiAgrupado in PublicadoresAgrupados:

        Provincias = []
        sql = "SElECT id_destino FROM publicador where id_padre =" + str(publiAgrupado[0]) + " group by id_destino"
        mycursor = conn.cursor()
        mycursor.execute(sql)
        destinoAgrupado = mycursor.fetchall()
        # if destinoAgrupado == 1:
        Provincias = []
        sql = "SElECT id_provincia FROM publicador where id_padre ="+str(publiAgrupado[0])+" group by id_provincia"
        mycursor = conn.cursor()
        mycursor.execute(sql)
        provinciasAgrupadas = mycursor.fetchall()

        for pronvicia in provinciasAgrupadas:
            Provincias.append(pronvicia[0])
        prov = ','.join(str(e) for e in Provincias)
        sql = "SElECT tema FROM publicador where id_padre =" + str(publiAgrupado[0]) + " group by tema"
        mycursor = conn.cursor()
        mycursor.execute(sql)
        temasAgrupados = mycursor.fetchall()

        for tema in temasAgrupados:
            try:
                sql = "SELECT link FROM todas_las_noticias where medio in " \
                      "(select link from portales_wordpress where id_provincia in("+prov+") )" \
                      "and link not in " \
                      "(select link from noticias_basura) " \
                      "and link not in " \
                      "(select link from noticias_enviadas_wordpress)" \
                      "and texto like "+'"%'+ tema[0]+'%"'
                mycursor = conn.cursor()
                mycursor.execute(sql)
                Portales = mycursor.fetchall()
            except Exception as e:
                print("Error al Obtener portales ", e)
            for link in Portales:
                try:
                    response2 = requests.get(link[0]).text
                    j = open("configParaWordpress.json", "r")
                    confiTagPage = {}
                    confiTagPage = json.loads(j.read())
                except Exception as e:
                    print("Error al Obtener el response ", e)
                nueva_entrada = WordPressPost()
                try:
                    for Noti in confiTagPage["j"]["imagenNoticia"]:

                            imagen = eval(Noti)
                            if imagen != []:
                                try:
                                    nueva_entrada.thumbnail = imagen
                                except Exception as e:
                                    print(e)
                except Exception as e:
                    print("Error al Obtener imagen ", e)
                try:

                    path = os.getcwd()+"\\00000001.jpg"
                    f = open(path, 'wb')
                    f.write(urllib.request.urlopen(nueva_entrada.thumbnail ).read())
                    f.close()

                    filename = path
                    data = {'name': 'picture.jpg', 'type': 'image/jpg', }
                    with open(filename, 'rb') as img:
                        data['bits'] = xmlrpc_client.Binary(img.read())

                    sql = "SElECT cw.usuario,cw.contraseña, cw.link FROM cuentas_wordpress as cw inner join publicador as p" \
                          " on cw.portal = p.url where p.id_padre =" + str(publiAgrupado[0]) + " group by 1,2,3"
                    mycursor = conn.cursor()
                    mycursor.execute(sql)
                    cuentas_wordpress = mycursor.fetchall()
                    usuario = cuentas_wordpress[0][0]
                    contraseña = cuentas_wordpress[0][1]
                    sitio = cuentas_wordpress[0][2]
                    cliente = Client(sitio, usuario, contraseña)
                    response = cliente.call(media.UploadFile(data))
                    imagenParaPublicar = response['id']
                    nueva_entrada.thumbnail = imagenParaPublicar
                    nueva_entrada.post_status = 'publish'

                    try:
                        for Noti in confiTagPage["j"]["tituloNoticia"]:

                            titulo = eval(Noti)
                            if titulo != []:
                                try:
                                    if len(titulo) > 3:
                                        nueva_entrada.title = titulo
                                except Exception as e:
                                    print(e)
                    except Exception as e:
                        print("Error al Obtener titulo noticia ", e)

                    try:
                        for Noti in confiTagPage["j"]["descripcionNoticia"]:

                            descripcion = eval(Noti)
                            if descripcion != []:
                                try:
                                    if len(descripcion) > 5:
                                        nueva_entrada.content = descripcion + "\n" + "Fuente: " + link[0] + ""
                                    else:
                                        nueva_entrada.content = "Fuente: " + link[0] + ""
                                except Exception as e:
                                    print(e)
                    except Exception as e:
                        print("Error al Obtener descripcion ", e)
                    try:
                        if not nueva_entrada.content or not nueva_entrada.title or not nueva_entrada.thumbnail:
                            break
                        # nueva_entrada.title = titulo
                        # nueva_entrada.content = texto
                        # nueva_entrada.terms_names = {
                        # 'post_tag': ['AI', 'musk'],
                        # 'category': ['Technology', 'Chemistry']}
                        id_entrada_publicada = cliente.call(posts.NewPost(nueva_entrada))
                    except Exception as e:
                        print("Error consulta", e)
                    try:
                        mycursor = conn.cursor()
                        sql = "INSERT INTO noticias_enviadas_wordpress (link, titulo, descripcion,tema,campaña,nombreWordPress) " \
                              "VALUES (%s, %s, %s, %s, %s, %s)"
                        val = (link[0], nueva_entrada.title, nueva_entrada.content, "", "", usuario)
                        mycursor.execute(sql, val)
                        conn.commit()
                    except Exception as e:
                        print(e)
                    print("Correcto! Se publicó la entrada, y su id es {}".format(id_entrada_publicada))

                except Exception as e:
                    print("Error al Obtener informacion del wordpress ", e)






