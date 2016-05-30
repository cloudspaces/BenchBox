'''
dado un fichero pcap, parsear el log pcap

clasificar por paquetes por protocolo puerto y metadato dato.

generar un json estadistico, este json se envia al mongodb del manager

anadir una opcion en el manager para descargarse un archivo estadistico con formato json y generar grafica estatic.

o insertar lo en influx db como atributos de una medida?


sub-domain Data-center Description
client-lb/clientX       Dropbox Meta-data
notifyX                 Dropbox Notifications
api                     Dropbox API control
www                     Dropbox Web servers
d                       Dropbox Event logs
dl                      Amazon Direct links
dl-clientX              Amazon Client storage
dl-debugX               Amazon Back-traces
dl-web                  Amazon Web storage
api-content             Amazon API Storage

-- py_metadata counter =>

values = {
metadata:
data:
notification:
}


sendCurrentCounter() => thread

loop()






'''


'''

probar en local: >> maquina virtual sandbox

PARTE 1

1r lanzar cliente stacksync

2n lanzar cliente dropbox

PARTE 2

encontrar la pid de stacksync y dropbox

PARTE 3

distinguir que puertos utilizan cada personalcloud para gestionar los datos y metadatos,
poner un contador de paquetes y sumador de bytes.
... no se sabe

PARTE 4

entre start y stop generar nueva cabecera pcap por timestamp, client, profile, hostname.

PARTE 5



'''