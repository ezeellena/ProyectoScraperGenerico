import datetime
import json
import pickle
import urllib
import requests
import csv
import re
import os
from unidecode import unidecode
from bs4 import BeautifulSoup
from openpyxl import Workbook
from nube import texto2els
import sys
from store import store


nrogrupo = ""
path = ""

import hashlib

def hashear(l):
    l = l.encode('utf-8')
    h = hashlib.new( "sha1",l)
    return h.hexdigest()
def link2medio(link):
    r = ""
    try:
        r  = re.search( '(?<=www.)\w+', link ).group()
    except:
        try:
            r = re.search( '(?<=//)\w+', link ).group()
        except:
            r =""
            return r
    return r
def actualizar_tema(grupo_telegram, tema_anterior):

    try:
        grupo_telegram = grupo_telegram.lower()


        # me conecto a la API de Sonda para ver que tema tiene asignado cada grupo
        url = "http://167.86.120.98:5002/sb_get_tema/?grupo="+grupo_telegram
        r = requests.get(url).text

        if tema_anterior != ",".join(eval(r)):
            enviar_noticias(["----------------\n"
                             "--" + grupo_telegram +
                             "\n *El término de búsqueda ahora es:* \n"+ r +""
                             "\n-------------"])

        return r
    except Exception as e:
        return "-1"
j_link_enviado = {}
j_pag_ne = {}
mugre = ["xmlns=http://www.w3.org/1999/>", "<\n", "\n>", "<<p>", "<p>", "</p", "xmlns=http://www.w3.org/1999/>",
         "xmlns=http://www.w3.org/1999/>", "<br />", "CDATA", "</div>>", "<div>", "</div>", "%>", "<iframe>",
         "</iframe>", "100%", "<div", "http://w3.org/", "xmlms", "xhtml", ";>", "<", ">", "'", '"', "\/", "]", "[",
         "/","-","ttp",":","swww"]
def limpiar(texto, mugre):
    for m in mugre:
        texto = texto.replace(m, "")
    return texto
def link_enviado(l):

    print("Telegram analiza este link para enviar ",l)
    l = limpiar(l, mugre)
    l = hashear(l)

    if not l in j_link_enviado.keys():
        print(" Enviando a telegram :", l)
        j_link_enviado[l] = 1
        return False
    else:
        print(" !!!!!!!!!!!!!!! ENCONTRO DUPLICADO !!!!!!!!!!!!!!!!!! ")
        return True
def log(texto):
    l = open("log.csv", "a")
    l.write(texto + "\n")
    l.close()
def save_persist(elem):
    try:
        vpath = "./persist"+nrogrupo+"/"

        varchivo = vpath + elem + ".bin"
        with open(varchivo, "bw") as archivo:
            pickle.dump(eval(elem), archivo)
    except Exception as e:

        print("Except de save_persist", e)
def load_persist(elem):
    try:

        vpath = "./persist"+nrogrupo+"/"
        varchivo = vpath + elem + ".bin"

        with open(varchivo, "br") as archivo:
            # #print(pickle.load(archivo))
            return pickle.load(archivo)

    except Exception as e:

        print("269 - Except load_persit ", e)
def replaceBase(texto):
    texto = texto.replace("http:", " ").replace("//", " ").replace(".", " ").replace("www", " ").replace(
            "https:", " ").replace("/", " ").replace("\n", " ").replace("-", " ")
    return  texto
def replaceURL(texto):
    texto = texto.replace("http:", "").replace("//", "").replace(".", "").replace("www", "").replace(
            "https:", "").replace("/", "").replace("\n", "").replace("-", "")
    return  texto
def contarElementosLista(lista):
    """
    Recibe una lista, y devuelve un diccionario con todas las repeticiones decada valor
    """
    return {i:lista.count(i) for i in lista}

class RSSParser(object):

    def parse(self,confiTagPage, urlytag, tema):
        ListaDeLinks = []
        items = []
        Noticia = []
        RedesSociales = ["facebook", "twitter", "whatsapp"]
        self.url = urlytag
        global urlCortada
        if "news.google" in urlytag:
             urlCortada = "Google"
        else:

            urlCortada= replaceURL(urlytag)
        LINKS = open("./LINKS/" + urlCortada + ".csv", "a", encoding='utf-8')

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
            }
            response = requests.get(url, headers=headers).text
        except Exception as e:
            print("Error 1 - Obtener Response ", e)
        fila = 0
        try:
            LINKS.write('----------LINK-----------' + '\n' + str(url) + '\n')
            for Noti in confiTagPage["j"]["BuscarNoticia"]:
                         
                try:
                    Noticias = eval(Noti)
                    fila += 1
                    if Noticias != []:
                        LINKS.write('----------EVALUADOR-----------:' + '\n' + str(Noti) + '\n')
                        for i, Noticiae in enumerate(Noticias):
                            texto = filtroReplace(Noticiae.get_text())
                            if filtro_tema2(texto, tema) and texto != '':
                                Noticia.append(Noticiae)
                                LIIINKS = [a['href'] for a in Noticiae.find_all('a', href=True)]
                                # LIIINKS = ', '+'\n'.join(LIIINKS)
                                print(LIIINKS)
                                LINKS.write(
                                    '----------HTML-----------:' + '\n' + str(filtroReplace(Noticiae.text)) + '\n')
                                LINKS.write('----------LINK-----------:' + '\n' + str(LIIINKS) + '\n')

                                                                                                                      
                except Exception as e:
                                                                          
                                                                                           
                    print("Error 2 - Obtener Articulos de noticias ", e)

        except Exception as e:
            print("Error 3 - Obtener Articulos de noticias ", e)
        temp9 = ""
        row = 3
        try:
            for i in Noticia:
                row +=1

                texto = filtroReplace(i.get_text())
                if filtro_tema2(texto, tema) and texto != '':

                    ListaDeLinks = eval(confiTagPage["j"]["path"])
                    if ListaDeLinks != "":
                        SetDeLinks = set(ListaDeLinks)
                        url2 = url
                        try:
                            resultado = contarElementosLista(ListaDeLinks)
                            if resultado != {}:
                                maximo = max(resultado, key=resultado.get)
                                print("El valor mas repetido es el ", maximo, " con ", resultado[maximo], " veces")

                        except Exception as e:
                            print(" 4 - Obtener Resultado maximo de links ", e)
                        if len(SetDeLinks) == 1 and list(SetDeLinks)[0] != urlytag:
                            temp9 = list(SetDeLinks)
                            temp9 = str(temp9[0])
                            LINKS.write('----------LINK-----------'+'\n'+ str(unidecode(temp9))+'\n'+  '----------HTML-----------:' +'\n'+ unidecode(str(texto)) +  '\n')
                        else:
                            if resultado != {}:
                                if resultado[maximo] >= 2:
                                    temp9 = maximo
                                    LINKS.write('----------LINK-----------' + '\n' + str(unidecode(
                                        temp9)) + '\n' + '----------HTML-----------:' + '\n' + unidecode(str(
                                        texto)) + '\n')
                                else:
                                    palabras = texto.split()
                                    palabras.append(tema)
                                    try:
                                        for l in ListaDeLinks:
                                            linkCortado = replaceBase(l).split()
                                            totalPalabras = len([palabra for palabra in palabras if palabra in linkCortado])
                                            if 2 <= totalPalabras <= 20:
                                                totalRedes = len([redSocial for redSocial in RedesSociales if redSocial in l.lower()])
                                                if not totalRedes >= 1:
                                                    temp9 = l
                                                    LINKS.write(unidecode(temp9) + '\n')

                                    except Exception as e:
                                        print(" ERROR 5 - NO ESCRAPEO NADA ", e)
                                        print(" ********* URL no parseada correctamente: \n", url, "\n")
                                        print(i)
                                        print("**********************************************************")

                                        if not i.text in j_pag_ne.keys():
                                            j_pag_ne[i.text] = 1
                                            log("***** \n No scrapeó esta página: \n" + url + '\n' + str(i) + '\n ********')


                            """
                            print("- url: ", url)
                            print("- temp9:" , temp9)
                            print("--------------------------------")
                        """
                    if temp9[:1] == "/":
                        temp9 = temp9[1:]
                    if temp9[:2] == "./":
                        temp9 = temp9[2:]
                    if temp9[:8] == "noticias":
                        temp9 = temp9[8:]
                    if "http" in temp9:
                        url2 = temp9
                        temp9 = ""

                            # print(" url final:  ", url +  temp9 + temp10 + temp11, "\n temp9: ", temp9, "\n temp10: ",temp10, "\n temp11: ",temp11, "\n temp12: ",temp12)
                    if "news.google" in url2:
                        url2 = "https://news.google.com/"
                    j_i = {"link": url2 + temp9,
                           "desc": texto,
                           "tmpItems": i}
                    try:
                        if not filtro_repetida(j_i):
                            #archivoCSV = []
                            LinkNotcia = j_i["link"]
                            #DescripcionNoticia = ""
                            #fechaPublicacion = ""
                            #response2 = requests.get(LinkNotcia, headers=headers).text

                            """ 
                                                       Titulo = []
                                                        for Titu in confiTagPage["j"]["tituloNoticia"]:
                                                            try:
                                                                Titulos = eval(Titu)
                                                                if Titulos != []:
                                                                    Titulo.append(Titulos)
                                                            except Exception as e:
                                                                print(" Obtener Titulo", e,Titu)
                                                        resultadoTitulo = contarElementosLista(Titulo)
                                                        if resultadoTitulo != {}:
                                                            maximoTitulo = max(resultadoTitulo, key=resultadoTitulo.get)
                                                            print("El valor mas repetido es el ", maximoTitulo, " con ", resultadoTitulo[maximoTitulo], " veces")

                                                        Descripcion = []
                                                        for Descr in confiTagPage["j"]["descripcionNoticia"]:
                                                            try:
                                                                Descripciones = eval(Descr)
                                                                if Descripciones != []:
                                                                    Descripcion.append(Descripciones)
                                                            except Exception as e:
                                                                print(" Obtener Titulo", e,Descr)
                                                        resultadoDescripcion = contarElementosLista(Descripcion)
                                                        if resultadoDescripcion != {}:
                                                            maximoDescripcion = max(resultadoDescripcion, key=resultadoDescripcion.get)
                                                            #hoja.cell(row=row, column=7).value = maximoDescripcion
                                                            print("El valor mas repetido es el ", maximoDescripcion, " con ", resultadoDescripcion[maximoDescripcion], " veces")

                                                        link_web = url
                                                        FechaHoraScrapeo = str(datetime.datetime.now())
                                                        archivoCSV.append(link_web + ',\n' + ',\n' + LinkNotcia + ',\n' + FechaHoraScrapeo)


                                                        with open("out.csv", "a") as f:
                                                            wr = csv.writer(f, delimiter="\n")
                                                            for ele in items:
                                                                wr.writerow([ele + ","])
                                                        """
                    except Exception as e:
                        print( " ERROR AL OBTENER TITULO O DESCRIPCION", e )

                    items.append( LinkNotcia )

                    ### store the
                    #texto2els(texto, FechaHoraScrapeo, LinkNotcia)
                    link = LinkNotcia

                    # resto 5 horas porque es la diferencia horario que tengo con Alemania
                    #aive_dt = datetime.datetime.now() - - datetime.timedelta( hours=5)
                    #fecha = aive_dt.strftime( "%Y-%m-%dT%H:%M:%SZ" )


                    #titulo = maximoTitulo
                    # stract portal media from notice's link
                    #medio = link2medio(link)
                    #grupo = grupo_telegram_fijo

                    #store.store( titulo, fecha, texto, link, medio, grupo )

                    #########################################################################


            LINKS.close()
            #hojaExcelDeErrores.save('./Excel/errores' + urlCortada + '-Errores.xlsx')
            return items
        except Exception as e:
            print(" 100 - Obtener links ", e)
def filtroReplace(object):
    object.replace("/", "").replace(":", "").replace("%", "").replace("-", "").replace("[", "").replace("]","").replace("<","").replace(">", "").replace("!", "").replace(",", "")
    return " ".join(object.split())
def filtro_repetida(j_i):

    try:

        dd = j_i['link'].replace("\n", "")[1:200]
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
            print("\n ********* \n No encontrado: \n",dd,"\n",j_i['link'],"\n*************")
            save_persist('db_noticias2')
        return r


    except Exception as e:
        print("329 - ", e)
def filtro_tema(j_i, tema):
    c1 = tema.upper() in j_i['desc'].upper()
    for j in tema.split(","):
        c2 = j.upper() in j_i['desc'].upper()
        c1 = c1 or c2
    if c1:
        r = True
    else:
        r = False
    return r
def filtro_tema2(texto, tema):
    c1 = tema.upper() in texto.upper()
    for j in tema.split(","):
        c2 = j.upper() in texto.upper()
        c1 = c1 or c2
    if c1:
        r = True
    else:
        r = False
    return r
a_url_temas = []
def init():
    global vtelegram
    vtelegram = True

    def get_config(vkey):
        c = vkey in j_config.keys()
        if c:
            return j_config[vkey]
        else:
            return '-1'
def enviar_noticias(arr):
    if not vtelegram:
        pass
        # return
    filtro_repetida

    try:
        url_api = token + "/sendMessage"

        # print( "- tema \n", Tema, " \n ",  NombreGrupo )
        men_t = "✔ Noticias referidas al tema %s, enviadas al grupo de télegram %s: " % (Tema, NombreGrupo) + "\n"
        ta = False
        # recorro el arreglo de links y lo imprimos
        men = []
        # print("arr \n",  arr)
        # print( "men_t \n", men_t )
        for a in arr:
            # print("3- ",a)
            # men += "- " + a + "\n\n"

            # armo la linea
            l = "- " + a + "\n\n"
            men.append(l)
            if a != "":
                ta = True
        if ta:
            # Si tiene información, mando el título.
            requests.post('https://api.telegram.org/' + url_api, data={'chat_id': idchat, 'text': men_t})
            for m in men:

                # todo Eze, fijate que tuve que poner esta función par que controle no mandar repetidos.
                if not link_enviado(m):

                    requests.post('https://api.telegram.org/' + url_api,
                                  data={'chat_id': idchat, 'text': '\n [' + NombreGrupo + ']\n' + m})
                    print(requests.status_codes)
    except Exception as e:
        print(" 279 - enviar ", e)
def configuracion():


    f = open("configParametrosGenerico.json", "r")

    global j_config
    j_config = {}
    j_config = json.loads(f.read())
    global vtelegram
    global grupo_telegram_fijo
    grupo_telegram_fijo = j_config["grupo_telegram_fijo"]
    global url_api_sonda
    url_api_sonda = j_config["url_api_sonda"]

    try:
        vtelegram = j_config["telegram"]
    except:
        vtelegram = True
    global token
    token = j_config["token"]
    global idchat
    idchat = j_config["id_chat"]
    global Tema
    Tema = j_config["Tema"]
    global NombreGrupo
    NombreGrupo = j_config["NombreGrupo"]
    global directorio
    directorio = j_config["directorio"]
    try:

        global db_noticias2
        db_noticias2 = {}

        if os.path.isfile(directorio + 'persist'+nrogrupo+'/db_noticias2.bin'):
            db_noticias2 = load_persist("db_noticias2")
        else:
            db_noticias2 = {}
    except:
        db_noticias2 = {}

    try:
        global LinksDePaginasWeb
        LinksDePaginasWeb = {}
        if os.path.isfile(directorio + 'persist/LinksDePaginasWeb.bin'):
            LinksDePaginasWeb = load_persist("LinksDePaginasWeb")
        else:
            LinksDePaginasWeb = {}
    except:
        LinksDePaginasWeb = {}
def write_json(data, filename=path+'configGenerico.json'):
    with open(filename,'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":

    if len( sys.argv ) > 1:
        nrogrupo = sys.argv[3]

    configuracion()

    path = "./persist"+nrogrupo+"/"

    j = open("configGenerico2.json", "r")

    confiTagPage = {}
    confiTagPage = json.loads(j.read())
    urlNueva = ""


    if urlNueva != "":
        confiTagPage["j"]["link"].append(urlNueva)
        write_json(confiTagPage)


    result = actualizar_tema(grupo_telegram_fijo, Tema)
    if result != "-1":
        Tema = ",".join(eval(result))


    # setear datos de los argumentos

    if len( sys.argv ) > 1:

        idchat = sys.argv[1]
        NombreGrupo = sys.argv[2]
        print( " Argumentos: ", idchat, " ", NombreGrupo )

        grupo_telegram_fijo = NombreGrupo

        #input("presionar una tecla")



    while True:
        try:
            for url in confiTagPage["j"]["link"]:
                r = False
                if url in LinksDePaginasWeb.keys():
                    if (LinksDePaginasWeb[url] == 1):
                        r = True
                    else:
                        r = False
                if not r:
                    LinksDePaginasWeb[url] = 1
                    save_persist('LinksDePaginasWeb')
                if url != "":

                    ################################################################

                    # Actualizo el tema de búsqueda
                    result = actualizar_tema(grupo_telegram_fijo, Tema)
                    if result != "-1":
                        Tema = ",".join(eval(result))

                    # print( "********************************" )
                    print("TEMA:\n\n", Tema)
                    # print( "********************************" )
                    ##########################################################33
                    print(" Procesando la url:  ", url)
                    r = RSSParser().parse(confiTagPage, url, Tema)
                    if r != []:
                        enviar_noticias(r)
        except Exception as e:
            print("207 - problema en el for general ", e)
    fic.close()