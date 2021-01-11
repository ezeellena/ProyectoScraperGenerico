import json
import sys

from flask import Flask, request
import requests
import mysql.connector
from bs4 import BeautifulSoup
from tldextract import tldextract

mydb = mysql.connector.connect(
  host="167.86.120.98",
  port="3307",
  database="test_portales",
  user="root",
  password="dalas.2009"
)


def funcion_BuscaTitulo(linktitulo):
    try:
        titulo = BeautifulSoup(linktitulo, "html.parser").find("meta", {"property": "og:title"})["content"]
        return titulo
    except Exception as e:
        print("No Encontro titulo ", e)
    try:
        titulo = BeautifulSoup(linktitulo, "html.parser").find("meta", {"name": "og:title"})["content"]
        return titulo
    except Exception as e:
        print("No Encontro titulo ", e)
    try:
        titulo = json.loads(
            BeautifulSoup(linktitulo, "html.parser").find("script", {"type": 'application/ld+json'}).string)[
            "headline"]
        return titulo
    except Exception as e:
        print("No Encontro titulo ", e)
    try:
        titulo = json.loads(
            BeautifulSoup(linktitulo, "html.parser").find("script", {"type": 'application/ld+json'}).string)[0][
            "headline"]
        return titulo
    except Exception as e:
        print("No Encontro titulo ", e)
    try:
        titulo = BeautifulSoup(linktitulo, "html.parser").find("title").text
        return titulo
    except Exception as e:
        print("No Encontro titulo ", e)
def enviar_noticias(arr,id_chat,Nombre_Grupo,provincias,tema):

    try:
        url_api ="bot1477154971:AAHz2Ok9QD8bwzkAxIqqZc64GNPeqGjuRTI/sendMessage"
        temas = ''.join(tema)

        for m in arr:
            linkPortal = m[1]
            linkNoticia = m[0]
            mycursor = mydb.cursor()
            #sql = "SELECT * FROM noticias_enviadas WHERE link = '"+str(linkNoticia)+"'" +""+""
            #mycursor.execute(sql)
            #records = cursor.fetchall()
            #if  records == []:
            extracted = tldextract.extract(linkPortal)
            medio = "{}.{}".format(extracted.domain, extracted.suffix)
            medio = medio.replace(".com", "").replace(".ar", "")
            linktitulo = requests.get(m[0]).text
            titulo = funcion_BuscaTitulo(linktitulo)
            if isinstance(titulo, str):

                mensaje = "Medio: "+medio+"\n\n"+"    Última Noticia: " + titulo + "\n\n" + "    Ver más en ->" + linkNoticia
                requests.post('https://api.telegram.org/' + url_api,
                              data={'chat_id': id_chat, 'text': mensaje})
                print(requests.status_codes)
                try:
                    mycursor = mydb.cursor()
                    sql = "INSERT INTO noticias_enviadas (link,tema,id_grupo) " \
                          "VALUES (%s, %s, %s) "
                    val = (linkNoticia, temas, id_chat)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    print("insertó correctamente el link: " + linkNoticia + "")
                except Exception as e:
                    print("El Link ya fue guardado: " + linkNoticia + "")

    except Exception as e:
        print(" 279 - enviar ", e)
def corresponde_procesar_id(k, terminacion_id):
    if k[-2:] == terminacion_id:
        return True
    else:
        return False

if __name__ == '__main__':
    while True:
        terminacion_id = sys.argv[1]
        GruposDeTelegram = requests.get("http://167.86.120.98:6061/GrupoCanal").json()


        for Grupo in GruposDeTelegram["data"]:
            Provincias = []
            Temas = []
            resultado = []
            if Grupo["id_grupo"][-2:] == terminacion_id:
                ID_GRUPO = Grupo["id_grupo"]

                NombreDelGrupo = Grupo["nombre_grupo"]
                for pronvicia in Grupo["provincias"]:
                    Provincias.append(pronvicia["id_provincia"])
                prov = ','.join(str(e) for e in Provincias)
                for tema in Grupo["temas"]:
                    sql_select_Query = "SELECT link, medio, texto FROM todas_las_noticias WHERE texto like " \
                                       ""+'"%'+ tema["descripcion"]+'%"'+" and provincia in ("+ prov +") " \
                                    "and link not in (select link from noticias_enviadas  WHERE id_grupo = "+'"'+ ID_GRUPO+'"'+" " \
                                    "and tema = "+'"'+tema["descripcion"]+'"'+") and link not in (select link from noticias_basura)"
                    #sql_select_Query = "SELECT link, medio, texto FROM todas_las_noticias WHERE texto like '%"+ tema["descripcion"] \
                    # +"%' and provincia in ("+ prov +")"
                    cursor = mydb.cursor()
                    cursor.execute(sql_select_Query)
                    #records = cursor.fetchall()
                    resultado.extend(cursor.fetchall())
                    Temas = tema["descripcion"]
                    if not resultado == []:
                        enviar_noticias(resultado, ID_GRUPO, NombreDelGrupo, prov, Temas)







