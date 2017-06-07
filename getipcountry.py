#!/usr/bin/python
# coding: utf-8

import math
from urllib import FancyURLopener
import json
import sys
import time	
import os
import sqlite3
import getopt
from random import choice
PAIS='PA'
LACNIC="delegated-lacnic-latest"
user_agents = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'
]

class MyOpener(FancyURLopener, object):
    version = choice(user_agents)



def usage():

    comm = os.path.basename(sys.argv[0])

    if os.path.dirname(sys.argv[0]) == os.getcwd():
        comm = "./" + comm

    print "Usage: getipcountry options \n"
    print "       -c: Get Names of ASN and IP's"
    print "\nExamples:"
    print "        " + comm + " -c PA"
    print "        " + comm + " -c BO"
    print ""
    print "Countries:"
    print "             AR for Argentina"
    print "             BO for Bolivia"
    print "             BQ for Bonaire"
    print "             BR for Brasil"
    print "             BZ for Belize"
    print "             CL for Chile"
    print "             CO for Colombia"
    print "             CR for Costa Rica"
    print "             CU for Cuba"
    print "             CW for Curazao"
    print "             DO for Dominican Republic"
    print "             EC for Ecuador"
    print "             GF for Guyana Francesa"
    print "             GT for Guatemala"
    print "             GY for Guyana"
    print "             HN for Honduras"
    print "             HT for Haiti"
    print "             MX for Mexico"
    print "             NI for Nicaragua"
    print "             PA for Panama"
    print "             PE for Peru"
    print "             PY for Paraguay"
    print "             SR for Surinam"
    print "             SV for El Salvador"
    print "             SX for Sint Maarten"
    print "             TT for Trinidad y Tobago"
    print "             VE for Venezuela"


def checkifexist(asn):
    respuesta = False
    db = sqlite3.connect('LATAMBD')
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS latamips(id INTEGER PRIMARY KEY, country TEXT,nameorg TEXT, asns TEXT, networks TEXT, whoisraw TEXT)''')
    db.commit()
    cursor.execute('''SELECT asns from latamips''')
    all_rows = cursor.fetchall()
    for row in all_rows:
        numeros=row[0].split("|")
        for num in numeros:
            if((len(num) > 0 ) and (num == asn)):
                print "Se encontro el asn: "+num+" en la base de datos, Saltando"
                respuesta = True
    return respuesta

def showcountry(country):
    db = sqlite3.connect('LATAMBD')
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS latamips(id INTEGER PRIMARY KEY, country TEXT,nameorg TEXT, asns TEXT, networks TEXT, whoisraw TEXT)''')
    db.commit()
    consulta="SELECT * from latamips  where country='"+country+"'"
    cursor.execute(consulta)
    all_rows = cursor.fetchall()
    
    for row in all_rows:
        print "-------------------------------------------------------------------"
        print "Nombre: "+row[2]
        asns = row[3].split("|")
        networks = row[4].split("|")
        for nasn in asns:
            if len(nasn)>0:
                print "ASN: "+nasn
        for net in networks:
            if len(net)>0:
                print "Network: "+net

def storedb(country,nameorg,asns,networks):
    db = sqlite3.connect('LATAMBD')
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS latamips(id INTEGER PRIMARY KEY, country TEXT,nameorg TEXT, asns TEXT, networks TEXT, whoisraw TEXT)''')
    db.commit()
    try:
        with db:
            db.execute('''INSERT INTO latamips(country, nameorg, asns, networks) VALUES(?,?,?,?)''', (country,nameorg, asns, networks))
    except sqlite3.IntegrityError:
        print('Record already exists')
    finally:
        db.close()


def decode_data(data):
    global PAIS
    print "-----------------------------------------" 

    nombre = data['name']
    asns = ""
    networks = ""
    for entidad in data['entities']:
        if ( PAIS+"-"  in entidad['handle']):
            #print "Redes "
            #print entidad['networks']
            for red in entidad['networks']:
                networks=networks+"|"+red
            #print "Numero Sistemas Autonomos"
            for numaut in entidad['autnums']:
                asns=asns+"|"+numaut
    print "Nombre: "+nombre
    print "Redes: "+networks
    print "ASN: "+asns
    
    storedb(PAIS,nombre,asns,networks)


def urltodata(asn):
    bandera = True
    while bandera:
        abrirurl = MyOpener()
        #opener = urllib.FancyURLopener({})
        url = abrirurl.open("https://rdap.lacnic.net/rdap/autnum/"+asn)
        data = json.load(url)
        if ('name' in data):
            bandera = False
            return data        
        else:
            print "Se agotaron las peticiones, esperemos un cachito por favor"
        time.sleep(6)

def start(argv):
    global PAIS
    if len(sys.argv) < 3:
        usage()
        sys.exit()
    try:
        opts, args = getopt.getopt(argv, "c:s:")
    except getopt.GetoptError:
        usage()
        sys.exit()
    for opt, arg in opts:
        if opt == '-c':
            PAIS=arg
            getips(PAIS)
        if opt == '-s':
            PAIS=arg
            showcountry(PAIS)


def getips(country):
    global LACNIC
    global PAIS  
    file = open(LACNIC,"r")
    lines=file.readlines()
    for line in lines:
        if (('asn' in line) and (PAIS in line)):
            asn=line.split("|")
            if not (checkifexist(asn[3])):
                datos = urltodata(asn[3])
                decode_data(datos)



if __name__ == "__main__":
    try:
        start(sys.argv[1:])
    except KeyboardInterrupt:
        print "Search interrupted by user.."
    except:
        sys.exit()
