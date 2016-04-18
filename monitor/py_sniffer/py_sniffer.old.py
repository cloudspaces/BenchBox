#!/usr/bin/env python
import psutil, os, json, pcapy, socket, time, traceback, sys
import netifaces as ni
import whois
import time
import copy
from impacket.ImpactDecoder import EthDecoder
from threading import Thread
# from hurry.filesize import size
from time import gmtime, strftime

# global variable
global packet_index, transport_dict, network_dict, traffic_flow_dict, ip2hostname_cache
global my_ip, my_iface

my_iface = "eth0"


def get_time():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


def get_epoch_ms():
    return int(time.time()) *1000


def is_root():
    if os.getuid() == 0:
        print("r00thless!!! ")
    else:
        print("Cannot run as a mortal. ")
        sys.exit()


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_hostname_by_ip(ip):
    global ip2hostname_cache
    if ip in ip2hostname_cache:
        hostname = ip2hostname_cache[ip]
    else:  # cache it
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except:
            print ip
            # use whois to resolve this
            result = whois.whois(ip)
            emails = ''.join(result.emails)
            ip2hostname_cache[ip] = emails  # cannot be resolved, avoid resolving it again
            return emails
        ip2hostname_cache[ip] = hostname
    return hostname


def add_flow(src_host, dst_host, size):
    global traffic_flow_dict
    key = "{}_{}".format(src_host, dst_host)
    if key in traffic_flow_dict:
        traffic_flow_dict[key]['hit'] += 1
        traffic_flow_dict[key]['size'] += size
    else:
        traffic_flow_dict[key] = {"hit": 0, "size": 0}


"""
Thread que envia metainformacion de los paquetes por rabbit al manager
"""


class ReportAdapter(Thread):
    def __init__(self, client="dropbox", interval=5):
        self.client = client
        self.interval = interval
        self.exit = False

    def run(self):
        iteration = 0
        while not self.exit:
            print "Emit rabbit messages > [{}]{} ".format(self.client, iteration)
            time.sleep(self.interval)
            iteration += 1

    def exit(self):
        self.exit = True


'''
filter, given: client type

filter packet information

parsePacket()

'''

"""
Thread que extrea metainformacion de los paquetes y los clasifica segun cual sea el cliente de sincronizacion
"""


class FilterAdapter(object):
    def __init__(self, client="stacksync", server_ip="10.30.235.91", ):
        self.client = client
        self.server_ip = server_ip

    def parse_packet(self, packet):
        data_type = "data|metadata|notify"
        datagram_size = 0
        print "parse and classify information type"

        if self.client == "stacksync":
            print "Report Stacksync"
        elif self.client == "dropbox":
            print "Report Dropbox"
        return data_type, datagram_size


class TrafficMonitor(Thread):
    def __init__(self, iface="eth0", read_timeout=100, promiscuous=False, max_bytes=1024, packet_limit=-1):

        Thread.__init__(self)
        # pcapy.findalldevs() @ displays available network interfaces
        self.decoder = EthDecoder()
        self.max_bytes = max_bytes
        self.promiscuous = promiscuous  # not capture all the network traffice only the trafice toward current host
        self.read_timeout = read_timeout  # in milliseconds
        self.interface = iface

        #

        self.traffic_counter_old = {
            "idx": -1,
            "epoch": get_epoch_ms(),
            "total_up": {
                "c": 0,
                "size": 0
            },
            "total_down": {
                "c": 0,
                "size": 0
            },
            "data_up": {
                "c": 0,
                "size": 0
            },
            "data_down": {

                "c": 0,
                "size": 0
            },
            "meta_up": {

                "c": 0,
                "size": 0
            },
            "meta_down": {

                "c": 0,
                "size": 0
            },
            "comp_up": {

                "c": 0,
                "size": 0
            },
            "comp_down": {

                "c": 0,
                "size": 0
            },
            "misc_up": {

                "c": 0,
                "size": 0
            },
            "misc_down": {

                "c": 0,
                "size": 0
            }
        }

        self.traffic_counter = {
            "idx": -1,
            "epoch": get_epoch_ms(),
            "total_up": {
                "c": 0,
                "size": 0
            },
            "total_down": {
                "c": 0,
                "size": 0
            },
            "data_up": {
                "c": 0,
                "size": 0
            },
            "data_down": {

                "c": 0,
                "size": 0
            },
            "meta_up": {

                "c": 0,
                "size": 0
            },
            "meta_down": {

                "c": 0,
                "size": 0
            },
            "comp_up": {

                "c": 0,
                "size": 0
            },
            "comp_down": {

                "c": 0,
                "size": 0
            },
            "misc_up": {

                "c": 0,
                "size": 0
            },
            "misc_down": {

                "c": 0,
                "size": 0
            }
        }
        #
        self.traffic_port = {
            "server_in_port": {
                # {port: hit}
            },
            "client_in_port": {

            },
            "server_out_port": {
                # {port: hit}
            },
            "client_out_port": {

            }
        }
        # desktop client
        # setup capturer
        self.pc = pcapy.open_live("eth0", max_bytes, promiscuous, read_timeout)
        # self.notify_worker = None  # tread that will submit network information to the manager through rabbitmq
        self.notify_worker = None
        # setup filter


        self.desktop_client = "stacksync"

        # filter_ips = {
        #     "dropbox": ["10.30.236.141"],
        #     "stacksync": ["10.30.235.91", "10.30.236.141"]
        # }
        filter_ips = {
            "dropbox": [my_ip],
            "stacksync": ["10.30.235.91", my_ip]
        }

        # filter_ports = ["443", "5672", "5000", "8080"]  # stacksync ports

        filter_ports = {
            "dropbox": ["443"],
            "stacksync": ["5672", "5000", "8080"]
        }

        filter_opts = {
            "dropbox": "(host " + " && host ".join(filter_ips[self.desktop_client]) + ")",  # filter
            "stacksync": "(port " + " || port ".join(
                    filter_ports[self.desktop_client]) + ") && (host " + " || host ".join(
                    filter_ips[self.desktop_client]) + ")"  # filter

        }
        filter = filter_opts[self.desktop_client]
        print filter
        # filter = "(port " + " || port ".join(filter_ports) + ") && (host " + " || host ".join(filter_ips) + ")"  # filter

        self.pc.setfilter(filter)
        self.register = False
        self.pc.loop(packet_limit, self.__on_recv_pkts)

    def start_capture(self, interval=5, client="dropbox"):
        # depending the client we will apply one filter or another
        self.register = True
        if self.notify_worker is None:
            self.notify_worker = ReportAdapter(client=client, interval=interval)
            self.notify_worker.start()

    def stop_capture(self):
        self.register = False
        print "Wait notify_worker.join()"
        self.notify_worker.exit()
        self.notify_worker.join()
        print "Notify worker terminated!"
        self.notify_worker = None

    def update_traffic_counter_old(self):
        self.traffic_counter_old = copy.deepcopy(self.traffic_counter)

    def notify_stats(self):
        # todo report the stats over time since the last interval

        # elapsed time

        if self.traffic_counter["epoch"] == self.traffic_counter_old["epoch"]:
            print self.traffic_counter_old['idx'], self.traffic_counter['idx'], (self.traffic_counter["epoch"] - self.traffic_counter_old["epoch"])
            return None
        # otherwise compute diff
        elapsed_time = float(self.traffic_counter["epoch"] - self.traffic_counter_old["epoch"]) # have to cast this to float
        print elapsed_time
        #print self.traffic_counter
        #print self.traffic_counter_old
        # SIZE
        # data rate

        print self.traffic_counter["data_up"]["size"], self.traffic_counter_old["data_up"]["size"], elapsed_time
        data_up_size_rate = (self.traffic_counter["data_up"]["size"] - self.traffic_counter_old["data_up"]["size"]) / elapsed_time
        data_down_size_rate = (self.traffic_counter["data_down"]["size"] - self.traffic_counter_old["data_down"]["size"]) /elapsed_time
        # meta data rate
        meta_up_size_rate = (self.traffic_counter["meta_up"]["size"] - self.traffic_counter_old["meta_up"]["size"]) /elapsed_time
        meta_down_size_rate = (self.traffic_counter["meta_down"]["size"] - self.traffic_counter_old["meta_down"]["size"])/elapsed_time

        # PACKET
        data_up_c_rate = (self.traffic_counter["data_up"]["c"] - self.traffic_counter_old["data_up"]["c"]) /elapsed_time
        data_down_c_rate = (self.traffic_counter["data_down"]["c"] - self.traffic_counter_old["data_down"]["c"]) /elapsed_time

        meta_up_c_rate = (self.traffic_counter["meta_up"]["c"] - self.traffic_counter_old["meta_up"]["c"]) /elapsed_time
        meta_down_c_rate = (self.traffic_counter["meta_down"]["c"] - self.traffic_counter_old["meta_down"]["c"]) /elapsed_time
        stats = {
            "data_rate": {
                "size_up": data_up_size_rate,
                "size_down": data_down_size_rate,
                "pack_up": data_up_c_rate,
                "pack_down": data_down_c_rate
            },
            "meta_rate": {
                "size_up": meta_up_size_rate,
                "size_down": meta_down_size_rate,
                "pack_up": meta_up_c_rate,
                "pack_down": meta_down_c_rate,
            }, "time": self.traffic_counter["epoch"]            # create timestamp
        }


        # self.traffic_counter_old = self.traffic_counter[:]
        self.update_traffic_counter_old()


        return stats["data_rate"], stats["meta_rate"]

    def __on_recv_pkts(self, ip_header, data):
        global packet_index

        # print ip_header
        # print "<<<<"
        # print "getts: {} getcaplen: {} getlen: {}".format(ip_header.getts(), ip_header.getcaplen(), ip_header.getlen())

        ether_packet = self.decoder.decode(data)
        total_size = ether_packet.get_size()
        packet_type = ether_packet.child()
        if packet_type.__class__.__name__ == "ARP":
            return None

        # print packet_type.__class__.__name__
        src_ip = packet_type.get_ip_src()
        dst_ip = packet_type.get_ip_dst()
        src_host = get_hostname_by_ip(packet_type.get_ip_src())
        dst_host = get_hostname_by_ip(packet_type.get_ip_dst())

        # print "get_header_size: {}".format(packet_type.get_header_size())  # ip header size, always 20 bytes
        # print "get_size: {}".format(packet_type.get_size())
        add_flow(src_host, dst_host, ether_packet.get_size())

        # TCP OR UDP
        packet_protocol = packet_type.child()
        packet_protocol_type = packet_protocol.__class__.__name__
        # print "{}[{}]".format(packet_protocol_type, packet_protocol.protocol)

        src_port = 0
        dst_port = 0
        data_size = packet_protocol.get_size()
        if packet_protocol.protocol == 17:
            # this is UDP
            # print "get_header_size: {}".format(packet_protocol.get_header_size())           # always 8 bytes
            # print "get_size: {}".format(packet_protocol.get_size())
            # print "get_uh_dport: {}".format(packet_protocol.get_uh_dport())                # todo:  dest port
            # print "get_uh_sport: {}".format(packet_protocol.get_uh_sport())                # todo:  source port
            src_port = packet_protocol.get_uh_sport()
            dst_port = packet_protocol.get_uh_dport()
        elif packet_protocol.protocol == 6:
            # this maybe TCP
            # print "get_header_size: {}".format(packet_protocol.get_header_size())
            # print "get_size: {}".format(packet_protocol.get_size())
            # print "get_th_dport: {}".format(packet_protocol.get_th_dport())
            # print "get_th_sport: {}".format(packet_protocol.get_th_sport())
            src_port = packet_protocol.get_th_sport()
            dst_port = packet_protocol.get_th_dport()
        elif packet_protocol.protocol == 1:
            # this is ICMP (Internet Controll Message)
            return None
        elif packet_protocol.protocol is None:
            return None
        else:
            # print packet_protocol.protocol
            raise NotImplemented

        # con todos los parametros aclarados hay que clasificarlo entre

        # data_up, data_down

        # metadata_up, metadata_down

        # notify_up, notify_down
        # print self.desktop_client

        ## classifica data & metadata per stacksync
        # print src_host, src_port, dst_host, dst_port, my_ip, src_ip, dst_ip

        packet_index += 1

        if self.desktop_client == "stacksync":  # private clouds you can distinguish by static_IP:static_PORT
            # print "is stacksync"
            flow = None
            if src_ip == my_ip:
                self.traffic_counter["total_up"]["size"] += total_size
                self.traffic_counter["total_up"]["c"] += 1
                flow = "up"
            elif dst_ip == my_ip:
                self.traffic_counter["total_up"]["size"] += total_size
                self.traffic_counter["total_up"]["c"] += 1
                flow = "down"

            if flow is None:  #
                return flow

            # print flow

            if flow == "down":
                if src_port == 8080:
                    # print "Data download {}".format(data_size)
                    self.traffic_counter["data_down"]["size"] += total_size
                    self.traffic_counter["data_down"]["c"] += 1
                elif src_port == 5672:
                    # print "Meta down {}".format(data_size)
                    self.traffic_counter["meta_down"]["size"] += total_size
                    self.traffic_counter["meta_down"]["c"] += 1
            else:
                if dst_port == 8080:
                    # print "Data upload {}".format(data_size)
                    self.traffic_counter["data_up"]["size"] += total_size
                    self.traffic_counter["data_up"]["c"] += 1
                elif dst_port == 5672:
                    # print "Meta upload {}".format(data_size)
                    self.traffic_counter["meta_up"]["size"] += total_size
                    self.traffic_counter["meta_up"]["c"] += 1

        elif self.desktop_client == "dropbox":
            # print "parse the request uri ...  preparar los dominios que havia en el paper en formato regexp"

            # print src_port
            # print dst_port
            if src_port == 443 or dst_port == 443:
                # print "Okey"
                pass
            else:
                # print "Not"
                return None  # not data nor metadata

            # print src_host
            # print dst_host
            flow = None

            if dst_port == 443:
                flow = "up"
                self.traffic_counter["total_up"]["size"] += total_size
                self.traffic_counter["total_up"]["c"] += 1
            elif src_port == 443:
                self.traffic_counter["total_down"]["size"] += total_size
                self.traffic_counter["total_down"]["c"] += 1
                flow = "down"

            if flow is None:  #
                return flow

            # print "the flow is: {}".format(flow)
            # data goes through
            if flow == "down":
                if "cloudfront" in src_host:
                    # im download from server == data down
                    self.traffic_counter["data_down"]["size"] += total_size
                    self.traffic_counter["data_down"]["c"] += 1
                elif "dropbox" in src_host:
                    self.traffic_counter["meta_down"]["size"] += total_size
                    self.traffic_counter["meta_down"]["c"] += 1
                elif "amazonaws" in src_host:
                    self.traffic_counter["data_down"]["size"] += total_size
                    self.traffic_counter["data_down"]["c"] += 1
                else:
                    # use whois to resole this
                    self.traffic_counter["misc_down"]["size"] += total_size
                    self.traffic_counter["misc_down"]["c"] += 1
            # elif flow == "up":
            else:
                if "cloudfront" in dst_host:
                    # im download from server == data down
                    self.traffic_counter["data_up"]["size"] += total_size
                    self.traffic_counter["data_up"]["c"] += 1
                elif "dropbox" in dst_host:
                    self.traffic_counter["meta_up"]["size"] += total_size
                    self.traffic_counter["meta_up"]["c"] += 1
                elif "amazon" in dst_host:
                    self.traffic_counter["data_up"]["size"] += total_size
                    self.traffic_counter["data_up"]["c"] += 1
                else:
                    # use whois to resolve this ip's # aqui no entrara nunca ni referenciando por ip
                    self.traffic_counter["misc_up"]["size"] += total_size
                    self.traffic_counter["misc_up"]["c"] += 1

        ## classifica data & metadata per dropbox
        '''
        print "{}:{}   ~>>~   {}:{}".format(src_host, src_port, dst_host, dst_port)
        print "Meta up:   {}".format(self.traffic_counter["meta_up"]["size"])
        print "Meta down: {}".format(self.traffic_counter["meta_down"]["size"])
        print "Data up:   {}".format(self.traffic_counter["data_up"]["size"])
        print "Data down: {}".format(self.traffic_counter["data_down"]["size"])
        print "Comp up:   {}".format(self.traffic_counter["comp_up"]["size"])
        print "Comp down: {}".format(self.traffic_counter["comp_down"]["size"])
        print "Misc up:   {}".format(self.traffic_counter["misc_up"]["size"])
        print "Misc down: {}".format(self.traffic_counter["misc_down"]["size"])
        print "Total up:   {}".format(self.traffic_counter["total_up"]["size"])
        print "Total down: {}".format(self.traffic_counter["total_down"]["size"])
        '''

        desc = "{0: >20}:{1: >6}   ~>>>{2: >10}>>>~   {3: >20}:{4: >6} {5: >5}".format(src_host, src_port, total_size,
                                                                                       dst_host, dst_port, flow)
        stat = "{0: >20}={1:>8} >> meta [{2: >10}/{3: >10}] data[{4: >10}/{5: >10}] total[{6: >10}/{7: >10}]".format(
            packet_index, get_time(),
            self.traffic_counter["meta_up"]["size"],
            self.traffic_counter["meta_down"]["size"],
            self.traffic_counter["data_up"]["size"],
            self.traffic_counter["data_down"]["size"],
            self.traffic_counter["total_up"]["size"],
            self.traffic_counter["total_down"]["size"]
            )

        # print desc
        print stat

        '''
        print "{}:{}   ~>>~   {}:{}".format(src_host, src_port, dst_host, dst_port)
        print "Meta up:   {}".format(sizeof_fmt(self.traffic_counter["meta_up"]["size"]))
        print "Meta down: {}".format(sizeof_fmt(self.traffic_counter["meta_down"]["size"]))
        print "Data up:   {}".format(sizeof_fmt(self.traffic_counter["data_up"]["size"]))
        print "Data down: {}".format(sizeof_fmt(self.traffic_counter["data_down"]["size"]))
        print "Comp up:   {}".format(sizeof_fmt(self.traffic_counter["comp_up"]["size"]))
        print "Comp down: {}".format(sizeof_fmt(self.traffic_counter["comp_down"]["size"]))
        '''

        dst_key = "{}:{}".format(dst_host, dst_host)
        src_key = "{}:{}".format(src_host, src_port)

        if src_host == my_ip:
            if src_key in self.traffic_port["client_out_port"]:
                self.traffic_port["client_out_port"][src_key] += 1
            else:
                self.traffic_port["client_out_port"][src_key] = 1
        else:
            if src_key in self.traffic_port["server_out_port"]:
                self.traffic_port["server_out_port"][src_key] += 1
            else:
                self.traffic_port["server_out_port"][src_key] = 1

        if dst_host == my_ip:
            if dst_key in self.traffic_port["client_in_port"]:
                self.traffic_port["client_in_port"][dst_key] += 1
            else:
                self.traffic_port["client_in_port"][dst_key] = 1
        else:
            if dst_key in self.traffic_port["server_in_port"]:
                self.traffic_port["server_in_port"][dst_key] += 1
            else:
                self.traffic_port["server_in_port"][dst_key] = 1

        # print self.traffic_port


        # print self.traffic_counter

        '''
        if self.register:
            print "packet received - REGISTERED"
        else:
            print "packet skipped"
        '''
        # print ip2hostname_cache
        # print traffic_flow_dict
        # print ">>>>"
        self.traffic_counter['epoch'] = get_epoch_ms()
        self.traffic_counter['idx'] = packet_index

        print self.notify_stats()

# -------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------

if __name__ == '__main__':
    is_root()

    packet_index = 0

    network_dict = {}  # type of layer one => IP, ARP, ICMP, IPX...     # internet
    transport_dict = {}  # type of layer two => TCP, UDP, SPX           # host to host

    # size_dict = {"hit": 0, "size": 0}      # size_dict[source] = [counter, size]

    traffic_flow_dict = {}  # traffic flow [src-host, dst-host] = #
    ip2hostname_cache = {}  # caching resolved ip to hostname

    skip_list = {
        '10.30.1.2': 'elrecerca.recerca.intranet.urv.es',
        '10.30.234.119': 'dhcp30-234-119.recerca.intranet.urv.es',
        '10.30.1.108': 'srect.recerca.intranet.urv.es'
    }

    # setup network setting
    my_ip = ni.ifaddresses(my_iface)[2][0]['addr']

    tm = TrafficMonitor()
    tm.start_capture()


    # envez de un bucle de print tener la opcion de print cuando se tecla
