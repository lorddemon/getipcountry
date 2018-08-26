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
database="LATAM_BD"
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


def checkifexist(handle):
    respuesta = False
    db = sqlite3.connect(database)
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS latamips(id INTEGER PRIMARY KEY, handle TEXT,country TEXT,nameorg TEXT, asns TEXT, network TEXT,network_start TEXT,network_end TEXT, ipVersion TEXT)''')
    db.commit()
    cursor.execute('''SELECT * from latamips where handle=?''',(handle,))
    all_rows = cursor.fetchall()
    print len(all_rows)
    if len(all_rows)!=0:
        print "ya existe registro de la organizacion "+handle
        respuesta = True
    return respuesta

def checkifexistNetwork(netw):
    var_net='"'+netw+'%'+'"'
    respuesta = False
    db = sqlite3.connect(database)
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS latamips(id INTEGER PRIMARY KEY, handle TEXT,country TEXT,nameorg TEXT, asns TEXT, network TEXT,network_start TEXT,network_end TEXT, ipVersion TEXT)''')
    db.commit()
    cursor.execute("SELECT * from latamips where network LIKE ?",(netw+'%',))
    all_rows = cursor.fetchall()
    if len(all_rows) > 0:
        print "Se encontro la red "+netw+" ya en la DB, saltando"
        respuesta = True
    return respuesta
def checkifexistAsn(asn):
    respuesta = False
    db = sqlite3.connect(database)
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS latamips(id INTEGER PRIMARY KEY, handle TEXT,country TEXT,nameorg TEXT, asns TEXT, network TEXT,network_start TEXT,network_end TEXT, ipVersion TEXT)''')
    db.commit()
    cursor.execute("SELECT * from latamips where asns LIKE ?",('%'+asn+'%',))
    all_rows = cursor.fetchall()
    if len(all_rows) > 0:
        print "Se encontro la asn "+asn+" ya en la DB, saltando"
        respuesta = True
    return respuesta



def showcountry(country):
    db = sqlite3.connect(database)
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS latamips(id INTEGER PRIMARY KEY, handle TEXT,country TEXT,nameorg TEXT, asns TEXT, network TEXT,network_start TEXT,network_end TEXT, ipVersion TEXT)''')
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

def storedb(handle,country,nameorg,asns,network,network_start,network_end,ipVersion):
    db = sqlite3.connect(database)
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS latamips(id INTEGER PRIMARY KEY, handle TEXT,country TEXT,nameorg TEXT, asns TEXT, network TEXT,network_start TEXT,network_end TEXT, ipVersion TEXT)''')
    db.commit()
    try:
        with db:
            db.execute('''INSERT INTO latamips(handle,country, nameorg, asns, network,network_start,network_end,ipVersion) VALUES(?,?,?,?,?,?,?,?)''', (handle,country, nameorg, asns, network,network_start,network_end,ipVersion))
    except sqlite3.IntegrityError:
        print('Record already exists')
    finally:
        db.close()


def decode_data(data):
    global PAIS
    print "-----------------------------------------" 

    asns = ""
    handle = ""
    country = ""
    nameorg = ""
    network = ""
    network_start = ""
    network_end = ""
    ipVersion = ""
    nameorg = data['vcardArray'][1][1][3]
    print "Nombre de la Organizacion: "+nameorg
    handle = data['handle']
    print "Identificador Entidad: "+handle
    country = data['vcardArray'][1][3][3][6]
    print "Pais: "+country


    for asn in data['autnums']:
        if 'handle' in asn:
            asns= asns+"|"+asn['handle']
        else:
            asns= asns+"|"
    print "ASNs Encontrados: "+asns
    countnetwork=0
    for networks in data['networks']:
        if 'handle' in networks:
            countnetwork=countnetwork+1
            print "Red "+str(countnetwork)
            print "Network: "+networks['handle']
            print "Direccion de Inicio: "+networks['startAddress']
            print "Direccion Final: "+networks['endAddress']
            storedb(handle,country,nameorg,asns,networks['handle'],networks['startAddress'],networks['endAddress'],networks['ipVersion'])
        else:
            print "No tiene redes"
            storedb(handle,country,nameorg,asns,"","","","")
    print "---------------------------------------------------------"
def getentitydata(entity):
    bandera = True
    while bandera:
        abrirurl = MyOpener()
        url= "https://rdap.lacnic.net/rdap/entity/"+entity
        print "GET "+url
        url = abrirurl.open(url)
        data = json.load(url)
        print data
        if 'handle' in data:
            bandera = False
            decode_data(data)
        elif 'nicbr_reverseDelegations' in data:
            print "Es Brasil"
        else:
            print "Se agotaron las peticiones, esperemos un momento por favor"
        time.sleep(6)
        print data

def getasndata(asn):
    bandera = True
    while bandera:
        abrirurl = MyOpener()
        url = "https://rdap.lacnic.net/rdap/autnum/"+asn
        print "GET "+url
        url = abrirurl.open(url)
        data = json.load(url)
        print data
        if 'handle' in data:
            bandera = False
            print "Se detecto la ASN de la entidad "+data['entities'][0]['handle']
            getentitydata(data['entities'][0]['handle'])
        else:
            print "Se agotaron las peticiones, esperemos un momento por favor"
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
            getasn(PAIS)
        if opt == '-s':
            PAIS=arg
            showcountry(PAIS)


def getasn(country):
    global LACNIC
    global PAIS  
    file = open(LACNIC,"r")
    lines=file.readlines()
    contador =0
    for line in lines:
        #if (('ipv' in line) and (PAIS =='ALL')):
        #    ip=line.split("|")
        #    datos = getipdata(ip[3])
        if (('asn' in line) and (PAIS in line)):
            contador=contador+1
            print contador
            asn=line.split("|")
            print asn[3]
            if not (checkifexistAsn(asn[3])):
                getasndata(asn[3])


if __name__ == "__main__":
    try:
        start(sys.argv[1:])
    except KeyboardInterrupt:
        print "Search interrupted by user.."
    except:
        sys.exit()
