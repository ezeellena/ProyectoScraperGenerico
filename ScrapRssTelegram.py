import sys
from datetime import time

import requests
import mysql.connector
from tldextract import tldextract

mydb = mysql.connector.connect(
  host="10.3.0.125",
  port="3307",
  database="test_portales",
  user="root",
  password="dalas.2009"
)

def enviar_noticias(resultado,id_chat,Nombre_Grupo,provincias,tema):

    try:
        url_api ="bot1477154971:AAHz2Ok9QD8bwzkAxIqqZc64GNPeqGjuRTI/sendMessage"
        temas = ''.join(tema)

        for m in resultado:
            titulo = m[1]
            linkNoticia = m[0]
            descripcion = m[2]
            contenido = m[3]
            extracted = tldextract.extract(linkNoticia)
            medio = "{}.{}".format(extracted.domain, extracted.suffix)
            medio = medio.replace(".com", "").replace(".ar", "")

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

if __name__ == '__main__':

        try:
            while True:
                try:
                    terminacion_id = sys.argv[1]
                    GruposDeTelegram = requests.get("http://stg.kernelinformatica.com.ar:6060/GrupoCanal").json()

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
                                try:
                                    sql_select_Query = "SELECT link, titulo, description, content FROM todas_las_noticias_rss " \
                                                       "WHERE (titulo like "+'"%'+ tema["descripcion"]+'%"'+" or  description like "+'"%'+ tema["descripcion"]+'%"'+" or content like "+'"%'+ tema["descripcion"]+'%"'+"  )" \
                                                    "and id_provincia in ("+ prov +") " \
                                                    "and link not in (select link from noticias_enviadas  WHERE id_grupo = "+'"'+ ID_GRUPO+'"'+" " \
                                                    "and tema = "+'"'+tema["descripcion"]+'"'+")"
                                    #sql_select_Query = "SELECT link, medio, texto FROM todas_las_noticias WHERE texto like '%"+ tema["descripcion"] \
                                    # +"%' and provincia in ("+ prov +")"
                                    cursor = mydb.cursor()
                                    cursor.execute(sql_select_Query)
                                    records = cursor.fetchall()
                                    resultado.extend(records)
                                except Exception as e:
                                    print("error mysql: " + str(e))
                                Temas = tema["descripcion"]
                                if not resultado == []:
                                    enviar_noticias(resultado, ID_GRUPO, NombreDelGrupo, prov, Temas)
                except Exception as e:
                    print("error: " + str(e))
                    time.sleep(2)
                    continue
        except Exception as e:
            print("error ultimo: " + str(e))
            time.sleep(2)

