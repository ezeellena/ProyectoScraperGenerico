import hashlib
import json
import os
import pickle
from datetime import date
import time
from urllib.parse import urlparse, urljoin
import colorama
import requests
import sys
import mysql.connector

from celery import Celery
CeleryClient = Celery('task_celery', broker='redis://default:d474210009@167.86.120.98:6379/0')

app = Celery('task_celery', broker='redis://default:d474210009@redis:6379/0')
from bs4 import BeautifulSoup
mydb = mysql.connector.connect(
  host="167.86.120.98",
  port="3307",
  database="test_portales",
  user="root",
  password="dalas.2009"
)
def configuracion(Id_Provincia):

    try:

        global db_noticias2
        db_noticias2 = {}

        if os.path.isfile('persist/db_noticias2'+Id_Provincia+'.bin'):
            db_noticias2 = load_persist("db_noticias2"+Id_Provincia+"")
        else:
            db_noticias2 = {}
    except:
        db_noticias2 = {}


mugre = ["xmlns=http://www.w3.org/1999/>", "<\n", "\n>", "<<p>", "<p>", "</p", "xmlns=http://www.w3.org/1999/>",
         "xmlns=http://www.w3.org/1999/>", "<br />", "CDATA", "</div>>", "<div>", "</div>", "%>", "<iframe>",
         "</iframe>", "100%", "<div", "http://w3.org/", "xmlms", "xhtml", ";>", "<", ">", "'", '"', "\/", "]", "[",
         "/","-","ttp",":","swww"]
def limpiar(texto, mugre):
    for m in mugre:
        texto = texto.replace(m, "")
    return texto
def hashear(l):
    l = l.encode('utf-8')
    h = hashlib.new( "sha1",l)
    return h.hexdigest()
def save_persist(elem,id_provincia):
    try:
        vpath = "./persist/"

        varchivo = vpath + elem + id_provincia + ".bin"
        with open(varchivo, "bw") as archivo:
            pickle.dump(eval(elem), archivo)
    except Exception as e:

        print("Except de save_persist", e)
def load_persist(elem,id_provincia):
    try:
        vpath = "./persist/"
        varchivo = vpath + elem + id_provincia+".bin"
        with open(varchivo, "br") as archivo:
            # #print(pickle.load(archivo))
            return pickle.load(archivo)
    except Exception as e:
        print("269 - Except load_persit ", e)
def filtro_repetida(link,Id_Provincia):
    try:
        dd = link.replace("\n", "")[1:200]
        dd = limpiar(dd, mugre)
        dd = hashear(dd)
        r = False
        if dd in db_noticias2.keys():
            if (db_noticias2[dd] == 1):
                r = True
            else:
                r = False
        if not r:
            db_noticias2[dd] = 1
            print("\n ********* \n No encontrado: \n",dd,"\n",link,"\n*************")
            save_persist('db_noticias2',Id_Provincia)
        return r
    except Exception as e:
        print("329 - ", e)
def filtroReplace(object):
    object.replace("/", "").replace(":", "").replace("%", "").replace("-", "").replace("[", "").replace("]","").replace("<","").replace(">", "").replace("!", "").replace(",", "")
    return " ".join(object.split())
def contarElementosLista(lista):
    return {i: lista.count(i) for i in lista}
def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)
def get_all_website_links(Portal,Noticiae):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()

    internal_urls = set()
    external_urls = set()
    # domain name of the URL without the protocol
    domain_name = urlparse(Portal).netloc
    #headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0', }
    #soup = BeautifulSoup(requests.get(url,headers=headers).content, "html.parser")
    for a_tag in Noticiae.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue
        # join the URL if it's relative (not absolute link)
        href = urljoin(Portal, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not is_valid(href):
            continue
        if href in internal_urls:
            continue
        if domain_name not in href:
            continue
        #print(f"{GREEN}[*] Internal link: {href}{RESET}")
        urls.add(href)
        internal_urls.add(href)
    return internal_urls



if __name__ == "__main__":

    if len( sys.argv ) > 1:
        Id_Provincia = sys.argv[1]
    colorama.init()

    GREEN = colorama.Fore.GREEN
    GRAY = colorama.Fore.LIGHTBLACK_EX
    RESET = colorama.Fore.RESET

    Portales = requests.get("http://167.86.120.98:6060/Portales?id_provincia="+Id_Provincia+"").json()
    j = open("configGenerico2.json", "r")

    confiTagPage = {}
    confiTagPage = json.loads(j.read())
    while True:
        try:
            for Portal in Portales:
                #Portal["url"] = 'https://rosarionuestro.com/'
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',}
                response = requests.get(Portal["url"], headers=headers).text
                try:
                    mycursor = mydb.cursor()

                    sql = "SELECT tag FROM portales_tag where portales like "+"'%"+ Portal["url"]+"%'" + ""
                    mycursor.execute(sql)
                    sql = mycursor.fetchall()
                except Exception as e:
                    print("Error al ejecutar la consulta")
                for Noti in sql:
                    try:

                        Noticia = eval(Noti[0])
                        if Noticia != []:
                            for i, Noticiae in enumerate(Noticia):
                                links = ""
                                CantLinks = ""

                                links = get_all_website_links(Portal["url"], Noticiae)
                                links = list(links)


                                CantLinks = contarElementosLista(links)
                                CantLinks = list(CantLinks)
                                if len(CantLinks) < 4:
                                    for link in CantLinks:

                                        timeinit = time.time()
                                        texto = filtroReplace(Noticiae.get_text())
                                        medio = Portal["url"]
                                        fecha = date.today()

                                        try:
                                            mycursor = mydb.cursor()
                                            sql = "INSERT INTO todas_las_noticias (link,fecha,titulo,copete,texto,medio,provincia) " \
                                                  "VALUES (%s, %s, %s, %s, %s, %s, %s) "
                                            val = (link, fecha, "", "", texto, medio, Id_Provincia)
                                            mycursor.execute(sql, val)
                                            mydb.commit()
                                            print("insertó correctamente el link: " + link + "")
                                        except Exception as e:
                                            print("El Link ya fue guardado: " + link + "")
                                        """
                                        try:
    
                                            val = (link, fecha, "", "", texto, medio, int(Id_Provincia))
                                            CeleryClient.send_task("task_celery.InsertNoticiaMySql", [{"val": val}])
                                        except Exception as e:
                                            print("El Link ya fue guardado: " + link + ", "+ str(e)+"")
                                        """
                                        timefin = time.time() - timeinit
                                        print(timefin)
                    except Exception as e:
                        print("Error 3 - Obtener Articulos de noticias ", e)
        except Exception as e:
            print("Error 3 - Obtener Articulos de noticias ", e)


