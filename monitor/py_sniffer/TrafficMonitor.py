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
import socket
# global variable

"""
Thread que envia metainformacion de los paquetes por rabbit al manager
"""

# meter todo lo relacionado al reporter aqui?
# como implementar el enlace de datos?


class TrafficMonitor(Thread):

    def __init__(self, iface="eth0", read_timeout=100, promiscuous=False, max_bytes=65535, packet_limit=-1, client="dropbox", server=None, port=None, reporter=False):

        if os.name == "nt":
            iface = "\\Device\\NPF_{EDB20D9F-1750-46D6-ADE7-76940B8DF917}"
            if iface == pcapy.findalldevs()[0]:
                print "OKEY"
            else:
                iface = pcapy.findalldevs()[0]
                print "WARNING!"

        if client.lower() == "stacksync" and server is None:
            print "server='server_ip' & port='server_port' are required!"
            sys.exit()
        super(TrafficMonitor, self).__init__()
        # to_ms # means buffering and lowering the amount of reads until filling the buffer or the timeout occurs instead of reading inmediately
        # Thread.__init__(self)
        # pcapy.findalldevs() @ displays available network interfaces
        self.is_reporter = reporter     # enable reporting thread to get values on under demand
        # if server is hostname format cast it to ip

        if server is None:
            self.sync_server_ip = None
        else:
            self.sync_server_ip = socket.gethostbyname(server)    # private syncronization server IP
        if os.name == "nt":
            self.is_windows = True
        else:
            self.is_windows = False
        self.sync_server_port = port
        self.desktop_client = client    # syncronization service name
        self.decoder = EthDecoder()     # packet decoder
        self.max_bytes = max_bytes      # maximum bytes ?
        self.promiscuous = promiscuous  # not capture all the network traffice only the trafice toward current host
        self.read_timeout = read_timeout  # in milliseconds
        self.interface = iface
        self.traffic_flow_dict = {}
        self.packet_index = 0
        self.transport_dict = {}
        self.network_dict = {}
        self.traffic_flow_dict = {}
        self.ip2hostname_cache = {}    #
        self.packet_limit = packet_limit
        self.register = None
        try:
            if os.name == "nt":
                self.my_ip = "10.0.2.15"  # static ip assignation inner image.
            else:
                self.my_ip = ni.ifaddresses(iface)[2][0]['addr']
        except KeyError:
            print "Interface not found!"
            sys.exit()


        self.traffic_counter_old = {
            "idx": -1,
            "epoch": self.get_epoch_ms(),
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
            "epoch": self.get_epoch_ms(),
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
        # setup capture
        self.is_root()


        # for each network interface
        # check regkey_value('HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\services\Tcpip\Parameters\Interfaces\{71AAC716-65BF-4942-9835-5BFECFE0CFC2}','IPAddress')

        #def __init__(self, iface="eth0", read_timeout=100, promiscuous=False, max_bytes=65535, packet_limit=-1, client="dropbox", server=None, port=None, reporter=False):
        self.pc = pcapy.open_live(self.interface, self.max_bytes, self.promiscuous, self.read_timeout)
        # '\\Device\\NPF_{EDB20D9F-1750-46D6-ADE7-76940B8DF917}',
        # '\\Device\\NPF_{71AAC716-65BF-4942-9835-5BFECFE0CFC2}'
        # self.notify_worker = None  # tread that will submit network information to the manager through rabbitmq
        self.notify_worker = None
        # setup filter

        # snaplen specifies the maximum number of bytes to capture.
        # If this value is less than the size of a packet that is captured, only the first snaplen bytes of that packet will be captured and provided as packet data. A value of 65535

        filter_ips = {
            "dropbox": [self.my_ip],
            "stacksync": [self.sync_server_ip, self.my_ip],
            "mega": [self.my_ip],
            "owncloud": [self.my_ip, self.sync_server_ip]
        }

        # filter_ports = ["443", "5672", "5000", "8080"]  # stacksync ports

        filter_ports = {
            "dropbox": ["443"],  # ssl connection, serverside data and metadata
            "stacksync": [self.sync_server_port,   # rabbit
                          "5000",   # login
                          "8080"],   # data => swift
            "mega": ["443"],  # habria que comprobar que puertos utilizan, pero vamos a suponer que son todos 443
            "owncloud": ["8080"]  # habria que averiguar manualmente que puertos usar
        }

        filter_opts = {
            "dropbox":   "(port " + " || port ".join(filter_ports[self.desktop_client]) + ") && "
                    "(host " + " && host ".join(filter_ips[self.desktop_client]) + ")",  # filter
            "stacksync": "(port " + " || port ".join(filter_ports[self.desktop_client]) + ") && "
                    "(host " + " || host ".join(filter_ips[self.desktop_client]) + ")",  # filter
            "mega":  "(host " + " || host ".join(filter_ips[self.desktop_client]) + ")",  # filter
            "owncloud": "(host " + " || host ".join(filter_ips[self.desktop_client]) + ")"  # filter

        }
        filter = filter_opts[self.desktop_client]
        print ""
        print "filter: "
        print filter
        print ""
        self.pc.setfilter(filter)

    def get_hostname_by_ip(self, ip):
        if ip in self.ip2hostname_cache:
            hostname = self.ip2hostname_cache[ip]
        else:  # cache it
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except:
                # use whois to resolve this
                result = whois.whois(ip)
                emails = ''.join(result.emails)
                self.ip2hostname_cache[ip] = emails  # cannot be resolved, avoid resolving it again
                print ip, emails    # unresolvable ip => into email (support)
                return emails
            self.ip2hostname_cache[ip] = hostname
        return hostname

    def add_flow(self, src_host, dst_host, size):
        key = "{}_{}".format(src_host, dst_host)
        if key in self.traffic_flow_dict:
            self.traffic_flow_dict[key]['hit'] += 1
            self.traffic_flow_dict[key]['size'] += size
        else:
            self.traffic_flow_dict[key] = {"hit": 0, "size": 0}

    def cancel(self):
        '''
        Cancels this thread class
        :return:
        '''
        self.cancelled = True

    def run(self, interval=5, client="dropbox"):
        print "START CAPTURE"
        self.register = True
        # depending the client we will apply one filter or another
        thread = Thread(target=self.pc.loop, args=[self.packet_limit, self.__on_recv_pkts])
        thread.start()
        # infinite loop capturing and updating packet counters
        print "Capturing"

    def stop_capture(self):
        self.register = False
        print "Wait notify_worker.join()"
        self.cancel()

    def update_traffic_counter_old(self):
        self.traffic_counter_old = copy.deepcopy(self.traffic_counter)

    def notify_stats(self):
        # todo report the stats over time since the last interval
        # elapsed time
        '''
        if self.traffic_counter["epoch"] == self.traffic_counter_old["epoch"]:
            print self.traffic_counter_old['idx'], self.traffic_counter['idx'], (self.traffic_counter["epoch"] - self.traffic_counter_old["epoch"])
            return {
                "data_rate": {
                    "size_up": 0,
                    "size_down": 0,
                    "pack_up": 0,
                    "pack_down": 0
                },
                "meta_rate": {
                    "size_up": 0,
                    "size_down": 0,
                    "pack_up": 0,
                    "pack_down": 0,
                }, "time": self.traffic_counter["epoch"]            # create timestamp
            }
        '''
        # otherwise compute diff
        elapsed_time = float(self.traffic_counter["epoch"] - self.traffic_counter_old["epoch"]) # have to cast this to float
        # print elapsed_time
        # SIZE
        # data rate
        # print self.traffic_counter["data_up"]["size"], self.traffic_counter_old["data_up"]["size"], elapsed_time
        '''
        data_up_size_rate = ((self.traffic_counter["data_up"]["size"] - self.traffic_counter_old["data_up"]["size"]) / elapsed_time) * 1000
        data_down_size_rate = ((self.traffic_counter["data_down"]["size"] - self.traffic_counter_old["data_down"]["size"]) /elapsed_time ) * 1000
        # meta data rate
        meta_up_size_rate = ((self.traffic_counter["meta_up"]["size"] - self.traffic_counter_old["meta_up"]["size"]) /elapsed_time) * 1000
        meta_down_size_rate = ((self.traffic_counter["meta_down"]["size"] - self.traffic_counter_old["meta_down"]["size"])/elapsed_time) * 1000
        # PACKET
        data_up_c_rate = ((self.traffic_counter["data_up"]["c"] - self.traffic_counter_old["data_up"]["c"]) /elapsed_time) * 1000
        data_down_c_rate =((self.traffic_counter["data_down"]["c"] - self.traffic_counter_old["data_down"]["c"]) /elapsed_time) * 1000
        meta_up_c_rate = ((self.traffic_counter["meta_up"]["c"] - self.traffic_counter_old["meta_up"]["c"]) /elapsed_time) * 1000
        meta_down_c_rate = ((self.traffic_counter["meta_down"]["c"] - self.traffic_counter_old["meta_down"]["c"]) /elapsed_time) * 1000
        '''
        # just get the increment of each notify
        data_up_size_rate = (self.traffic_counter["data_up"]["size"] - self.traffic_counter_old["data_up"]["size"])
        data_down_size_rate = (self.traffic_counter["data_down"]["size"] - self.traffic_counter_old["data_down"]["size"])
        # meta data rate
        meta_up_size_rate =(self.traffic_counter["meta_up"]["size"] - self.traffic_counter_old["meta_up"]["size"])
        meta_down_size_rate = (self.traffic_counter["meta_down"]["size"] - self.traffic_counter_old["meta_down"]["size"])
        # PACKET
        data_up_c_rate = (self.traffic_counter["data_up"]["c"] - self.traffic_counter_old["data_up"]["c"])
        data_down_c_rate =(self.traffic_counter["data_down"]["c"] - self.traffic_counter_old["data_down"]["c"])
        meta_up_c_rate = (self.traffic_counter["meta_up"]["c"] - self.traffic_counter_old["meta_up"]["c"])
        meta_down_c_rate = (self.traffic_counter["meta_down"]["c"] - self.traffic_counter_old["meta_down"]["c"])

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
        return stats

    def __on_recv_pkts(self, ip_header, data):


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
        src_host = self.get_hostname_by_ip(packet_type.get_ip_src())
        dst_host = self.get_hostname_by_ip(packet_type.get_ip_dst())

        # print "get_header_size: {}".format(packet_type.get_header_size())  # ip header size, always 20 bytes
        # print "get_size: {}".format(packet_type.get_size())
        self.add_flow(src_host, dst_host, ether_packet.get_size())

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
        # print src_host, src_port, dst_host, dst_port, src_ip, dst_ip

        self.packet_index += 1

        if self.desktop_client == "stacksync":  # private clouds you can distinguish by static_IP:static_PORT
            # print "is stacksync"
            flow = None
            if src_ip == self.my_ip:
                self.traffic_counter["total_up"]["size"] += total_size
                self.traffic_counter["total_up"]["c"] += 1
                flow = "up"
            elif dst_ip == self.my_ip:
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

            if flow is None:  # else: unknown flow
                return flow

            # print "the flow is: {}".format(flow)
            # data goes through
            if flow == "down":
                if "d.v.dropbox.com" in src_host:
                    self.traffic_counter["meta_down"]["size"] += total_size
                    self.traffic_counter["meta_down"]["c"] += 1
                elif "cloudfront" in src_host:
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

                if "d.v.dropbox.com" in dst_host:
                    self.traffic_counter["meta_up"]["size"] += total_size
                    self.traffic_counter["meta_up"]["c"] += 1
                elif "cloudfront" in dst_host:
                    # im download from server == data down
                    self.traffic_counter["data_up"]["size"] += total_size
                    self.traffic_counter["data_up"]["c"] += 1
                elif "dropbox" in dst_host:
                    self.traffic_counter["meta_up"]["size"] += total_size
                    self.traffic_counter["meta_up"]["c"] += 1
                elif "amazonaws" in dst_host:
                    self.traffic_counter["data_up"]["size"] += total_size
                    self.traffic_counter["data_up"]["c"] += 1
                else:
                    # use whois to resolve this ip's # aqui no entrara nunca ni referenciando por ip
                    self.traffic_counter["misc_up"]["size"] += total_size
                    self.traffic_counter["misc_up"]["c"] += 1




        elif self.desktop_client == "mega":
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

            if flow is None:  # else: unknown flow
                return flow

            # print "the flow is: {}".format(flow)
            # data goes through
            if flow == "down":
                if "karere.mega.nz" in src_host:
                    self.traffic_counter["meta_down"]["size"] += total_size
                    self.traffic_counter["meta_down"]["c"] += 1
                elif "api.mega.nz" in src_host:
                    self.traffic_counter["data_down"]["size"] += total_size
                    self.traffic_counter["data_down"]["c"] += 1
                else:
                    # use whois to resole this
                    self.traffic_counter["misc_down"]["size"] += total_size
                    self.traffic_counter["misc_down"]["c"] += 1
            # elif flow == "up":
            else:
                if "mega.nz" in dst_host:
                    self.traffic_counter["meta_up"]["size"] += total_size
                    self.traffic_counter["meta_up"]["c"] += 1
                elif "amazonaws" in dst_host:
                    self.traffic_counter["data_up"]["size"] += total_size
                    self.traffic_counter["data_up"]["c"] += 1
                else:
                    # use whois to resolve this ip's # aqui no entrara nunca ni referenciando por ip
                    self.traffic_counter["misc_up"]["size"] += total_size
                    self.traffic_counter["misc_up"]["c"] += 1



        ## classifica data & metadata per dropbox

        # print "{}:{}   ~>>~   {}:{}".format(src_host, src_port, dst_host, dst_port)
        '''
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

        '''
        desc = "{0: >20}:{1: >6}   ~>>>{2: >10}>>>~   {3: >20}:{4: >6} {5: >5}".format(src_host, src_port, total_size,
                                                                                       dst_host, dst_port, flow)
        stat = "{0: >20}={1:>8} >> meta [{2: >10}/{3: >10}] data[{4: >10}/{5: >10}] total[{6: >10}/{7: >10}]".format(
                self.packet_index, self.get_time(),
                self.traffic_counter["meta_up"]["size"],
                self.traffic_counter["meta_down"]["size"],
                self.traffic_counter["data_up"]["size"],
                self.traffic_counter["data_down"]["size"],
                self.traffic_counter["total_up"]["size"],
                self.traffic_counter["total_down"]["size"]
        )

        print desc
        print stat
        '''
        '''
        print "{}:{}   ~>>~   {}:{}".format(src_host, src_port, dst_host, dst_port)
        print "Meta up:   {}".format(sizeof_fmt(self.traffic_counter["meta_up"]["size"]))
        print "Meta down: {}".format(sizeof_fmt(self.traffic_counter["meta_down"]["size"]))
        print "Data up:   {}".format(sizeof_fmt(self.traffic_counter["data_up"]["size"]))
        print "Data down: {}".format(sizeof_fmt(self.traffic_counter["data_down"]["size"]))
        print "Comp up:   {}".format(sizeof_fmt(self.traffic_counter["comp_up"]["size"]))
        print "Comp down: {}".format(sizeof_fmt(self.traffic_counter["comp_down"]["size"]))
        '''

        # http://www.wired.com/2016/03/epic-story-dropboxs-exodus-amazon-cloud-empire/
        # voy a suponer que dropbox y amazon son datos
        # y ec son metadatos...

        dst_key = "{}:{}".format(dst_host, dst_host)
        src_key = "{}:{}".format(src_host, src_port)

        if src_host == self.my_ip:
            if src_key in self.traffic_port["client_out_port"]:
                self.traffic_port["client_out_port"][src_key] += 1
            else:
                self.traffic_port["client_out_port"][src_key] = 1
        else:
            if src_key in self.traffic_port["server_out_port"]:
                self.traffic_port["server_out_port"][src_key] += 1
            else:
                self.traffic_port["server_out_port"][src_key] = 1

        if dst_host == self.my_ip:
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
        self.traffic_counter['epoch'] = self.get_epoch_ms()
        self.traffic_counter['idx'] = self.packet_index

    @staticmethod
    def get_time():
        return strftime("%Y-%m-%d %H:%M:%S", gmtime())

    @staticmethod
    def get_epoch_ms():
        return int(time.time()) *1000

    @staticmethod
    def is_root():
        try:
            if os.getuid() == 0:
                print("r00thless!!! ")
            else:
                print("Cannot run as a mortal. ")
                sys.exit()
        except AttributeError:
            print "nt is ruthless, bypass rule is_root!!!"

    @staticmethod
    def sizeof_fmt(num, suffix='B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)



# only windows run this
# regkey_value('HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\services\Tcpip\Parameters\Interfaces\{71AAC716-65BF-4942-9835-5BFECFE0CFC2}','IPAddress')
'''
def regkey_value(path, name="", start_key = None):
    try:
        import winreg
    except:
        print "OS exception.."
        return

    if isinstance(path, str):
        path = path.split("\\")
    if start_key is None:
        start_key = getattr(winreg, path[0])
        return regkey_value(path[1:], name, start_key)
    else:
        subkey = path.pop(0)
    with winreg.OpenKey(start_key, subkey) as handle:
        assert handle
        if path:
            return regkey_value(path, name, handle)
        else:
            desc, i = None, 0
            while not desc or desc[0] != name:
                desc = winreg.EnumValue(handle, i)
                i += 1
            return desc[1]
'''
# -------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------



if __name__ == '__main__':

    # size_dict = {"hit": 0, "size": 0}      # size_dict[source] = [counter, size]
    '''
    skip_list = {
        '10.30.1.2': 'elrecerca.recerca.intranet.urv.es',
        '10.30.234.119': 'dhcp30-234-119.recerca.intranet.urv.es',
        '10.30.1.108': 'srect.recerca.intranet.urv.es'
    }
    '''

    # setup network setting
    if os.name == "nt":
        interface = '\\Device\\NPF_{EDB20D9F-1750-46D6-ADE7-76940B8DF917}'
    elif os.name == "posix":
        interface = "eth0"
    tm = TrafficMonitor(iface=interface, server="stacksync.urv.cat", port="5673", client="mega")
    tm.run() # intermediari que arranca trafficMonitor i permet realitzar get stats sobre la marcha o reiniciar el monitoreig
    while True:
        # print tm.notify_stats()
        time.sleep(5)
        # print tm.get_time()
    print "end"


    # envez de un bucle de print tener la opcion de print cuando se tecla


    # filter_ips = {
    #     "dropbox": ["10.30.236.141"],
    #     "stacksync": ["10.30.235.91", "10.30.236.141"]
    # }




    '''
    snaplen specifies the maximum number (max_bytes) of bytes to capture.
    If this value is less than the size of a packet that is captured,
    only the first snaplen bytes of that packet will be captured and provided as packet data.
    A value of 65535
    '''