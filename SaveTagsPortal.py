import json
import requests
import sys
import mysql.connector
from bs4 import BeautifulSoup
mydb = mysql.connector.connect(
  host="167.86.120.98",
  port="3307",
  database="test_portales",
  user="root",
  password="dalas.2009"
)
if __name__ == "__main__":


    numeros = [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    for Id_Provincia in numeros:
        Portales = requests.get("http://167.86.120.98:6060/Portales?id_provincia="+str(Id_Provincia)+"").json()
        j = open("configGenerico2.json", "r")

        confiTagPage = {}
        confiTagPage = json.loads(j.read())

        try:
            for Portal in Portales:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',}
                    response = requests.get(Portal["url"], headers=headers).text
                except Exception as e:
                    print("LINK NO FUNCIONA"+Portal["url"]+"", e)
                for Noti in confiTagPage["j"]["BuscarNoticia"]:
                    try:
                        Noticias = eval(Noti)
                        if Noticias != []:
                            try:
                                mycursor = mydb.cursor()
                                sql = "INSERT INTO portales_tag (portales,tag,id_provincia) " \
                                      "VALUES (%s, %s, %s) "
                                val = (Portal["url"], Noti, Portal["id_provincia"])
                                mycursor.execute(sql, val)
                                mydb.commit()
                                print("insertó correctamente el portal: " + Portal["url"] +"\n"+ "..tag.." + Noti +"\n"+ "..provincia.." + str(Portal["id_provincia"]) + "")
                            except Exception as e:
                                print(e,"\n"+"El Link ya fue guardado: " + Portal["url"] +"\n"+ "..tag.." + Noti +"\n"+ "..provincia.." + str(Portal["id_provincia"]) + "")
                    except Exception as e:
                        print("Error al Obtener Articulos de noticias ", e)
        except Exception as e:
            print("Error al Obtener Articulos de noticias ", e)