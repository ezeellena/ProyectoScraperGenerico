import re
import sys
import mysql.connector
import feedparser
mydb = mysql.connector.connect(
  host="167.86.120.98",
  port="3307",
  database="TestEze",
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
    try:
        while True:
            try:
                if len(sys.argv) > 1:
                    Id_Provincia = sys.argv[1]
                else:
                    Id_Provincia = "20"
                try:
                    sql_select_Query = "SELECT url from portales_rss where id_provincia="+Id_Provincia+""
                    cursor = mydb.cursor()
                    cursor.execute(sql_select_Query)
                    Portales = cursor.fetchall()
                except Exception as e:
                    print("error mysql: " + str(e))

                for Portal in Portales:
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',}
                        feed = feedparser.parse(Portal[0])
                        if feed:
                            for item in feed["items"]:
                                link = item["link"]
                                titulo = item["title"]
                                try:
                                    pubDate = item["published"]
                                except Exception as e:
                                    pubDate = item["updated"]
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
                        print("error en  feed"+ str(e) + "  "+  Portal[0])
                        f = open('log.txt', 'w')
                        f.write('error en  2do try - %s' % e)
                        f.close()
                        continue
            except Exception as e:
                print("error en  2do try" + str(e))
                f = open('log.txt', 'w')
                f.write('error en  2do try - %s' % e)
                f.close()
                continue
    except Exception as e:
        print("error en  1er try" + str(e))
        f = open('log.txt', 'w')
        f.write('error en  1er try - %s' % e)
        f.close()
