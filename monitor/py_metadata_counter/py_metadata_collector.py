#!/usr/bin/env python
import psutil
import netifaces as ni
import time, traceback, sys
import pcapy
from threading import Thread


'''

probar en local:

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
#-------------------------------------------------------------------------------
# Thread to capture the packets
#-------------------------------------------------------------------------------
class pcap_capture(Thread):
    def __init__(self, iface="eth0", pcap_name=""):
        Thread.__init__(self)

        #TODO: Parameters!
        #print ni.ifaddresses("eth0")[2]
        #print ni.ifaddresses("eth1")[2]
        ip = ni.ifaddresses(iface)[2][0]['addr']
        p = ["80", "443", "8080", "3128", "38088", "5672"]
        my_filter = "(port " + " || port ".join(p) + ") && (host " + ip + ")"

        self.stopit = False
        self.done = False
        self.bytes = 0
        self.packets = 0
        self.pcap = pcapy.open_live(iface, 1600, 1, 100)
        self.pcap.setfilter(my_filter)
        self.dumper = self.pcap.dump_open(pcap_name)

    def stop_flag(self):
        return self.stopit

    def get_bytes(self):
        return self.bytes

    def get_packets(self):
        return self.packets

    def call_back(self, header, data):
        self.packets += 1
        self.bytes += header.getlen()
        self.dumper.dump(header, data)

    def capture(self):
        while not self.stopit:
            self.pcap.dispatch(1, self.call_back)
        self.done = True

    def run (self):
        self.capture()

    def stop(self):
        self.stopit = True
        return self.done

#-------------------------------------------------------------------------------
# Main - For testing purposes
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print "py_metadata.py/START"
    print ni.ifaddresses("eth0")
    # start capturing the traffic
    worker = None
    try:
        capture = "/tmp/test.pcap"
        '''
        interface = sys.argv[1]
        worker = pcap_capture(interface=interface, capture=capture)
        '''
        worker = pcap_capture(pcap_name=capture)

        worker.daemon = True
        worker.start()
        time.sleep(30)
        print "packets:", worker.get_packets(), "bytes:", worker.get_bytes()
    except:
        traceback.print_exc(file=sys.stderr)
    while not worker.stop(): pass

    print "py_metadata.py/END"