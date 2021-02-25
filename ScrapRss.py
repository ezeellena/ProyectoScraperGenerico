import hashlib
import json
import os
import pickle
import re
from datetime import date
import time
from urllib.parse import urlparse, urljoin
import colorama
import requests
import sys
import mysql.connector
from celery import Celery
CeleryClient = Celery('task_celery', broker='redis://default:d474210009@167.86.120.98:6379/0')
import feedparser
app = Celery('task_celery', broker='redis://default:d474210009@redis:6379/0')
from bs4 import BeautifulSoup
mydb = mysql.connector.connect(
  host="10.3.0.125",
  port="3307",
  database="test_portales",
  user="root",
  password="dalas.2009"
)
# esto lo uso para limpiar los títulos y textos e basuras
mugre = ["rdquo;","&amp;","&gt",".ar",".com",";>>",";>","<br","&quot;","xmlns=http://www.w3.org/1999/>","<\n", "\n>","<<p>","<p>","</p","xmlns=http://www.w3.org/1999/>","xmlns=http://www.w3.org/1999/>","<br />","CDATA", "</div>>", "<div>", "</div>","%>", "<iframe>", "</iframe>", "100%", "<div", "http://w3.org/","xmlms","xhtml", ";>","]",'"',"'"]

def limpiar(texto, mugre):
    for m in mugre:
        texto = texto.replace(m,"")
    return texto
if __name__ == "__main__":

    if len(sys.argv) > 1:
        Id_Provincia = sys.argv[1]
    else:
        Id_Provincia = "5"
    Portales = requests.get("http://stg.kernelinformatica.com.ar:6060/Portales?id_provincia=" + Id_Provincia + "").json()

    for Portal in Portales:
        try:
            #Portal["url"] = 'https://rosarionuestro.com/'
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',}
            feed = feedparser.parse(Portal["url_rss"])
            if feed:
                for item in feed["items"]:
                    link = item["link"]
                    titulo = item["title"]
                    pubDate = item["published"]
                    description = limpiar(re.sub("<.*?>", "", item["summary"]),mugre)
                    try:
                        content = limpiar(re.sub("<.*?>", "", item["content"][0].value),mugre)
                    except Exception as e:
                        content = "No Contiene"
                    try:
                        mycursor = mydb.cursor()
                        sql = "INSERT INTO todas_las_noticias_rss (link,titulo,pubDate,description,content,id_provincia) " \
                              "VALUES (%s, %s, %s, %s, %s, %s) "
                        val = (link, titulo, pubDate, description, content,Id_Provincia)
                        mycursor.execute(sql, val)
                        mydb.commit()
                        print("insertó correctamente el link: " + link + "")
                    except Exception as e:
                        print("El Link ya fue guardado: " + link + "" + str(e.msg) + "")
        except Exception as e:
            print("error en  "+ str(e) + "  "+  Portal["url_rss"])