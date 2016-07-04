import os, sys
import pcapy
from impacket.ImpactDecoder import EthDecoder
import netifaces as ni
import socket
import time
from time import gmtime, strftime
import whois
import copy


class Sniff(object):

    def __init__(self, args):

        if os.name == "nt":
            self.platform_is_windows = True
            self.iface = "\\Device\\NPF_{EDB20D9F-1750-46D6-ADE7-76940B8DF917}"
            self.my_ip = "10.0.2.15"
        else:
            self.platform_is_windows = False
            self.iface = pcapy.findalldevs()[0]
            self.my_ip = ni.ifaddresses(self.iface)[2][0]['addr']

        if 'sync_server_ip' in args:
            # is not none
            self.sync_server_ip = socket.gethostbyname(args['sync_server_ip'])
        if 'sync_server_port' in args:
            # is not none
            self.sync_server_port = str(args['sync_server_port'])

        self.metric_conf = {"sync_server_port": 0,
                            "desktop_client": None,  # syncronization service name
                            "decoder": EthDecoder(),  # packet decoder
                            "max_bytes": 0,  # maximum bytes ?
                            "promiscuous": False,
                            # not capture all the network traffice only the trafice toward current host
                            "read_timeout": 0,  # in milliseconds
                            "interface": None,
                            "traffic_flow_dict": {},
                            "packet_index": 0,
                            "transport_dict": {},
                            "network_dict": {},
                            "traffic_flow_dict": {},
                            "ip2hostname_cache": {},  #
                            "packet_limit": 0,
                            "register": None}

        self.metric_prev = {
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
            }}

        self.metric_curr = {
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
            }}

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

        self.capture_filter_ips = []
        self.capture_filter_ports = []

        self.is_root()
        self.decoder = EthDecoder()     # packet decoder

        self.live_capture = pcapy.open_live(
            self.iface,
            args['max_bytes'],
            args['promiscuous'],
            args['read_timeout']
        )

        self.packet_limit = args['packet_limit']  # -1

        self.ip2hostname_cache = {}    #
        self.traffic_flow_dict = {}    #
        self.capture_thread = None
        self.packet_index = 0  # index of the captured packet

    def get_hostname_by_ip(self, ip):
        if ip in self.ip2hostname_cache:
            hostname = self.ip2hostname_cache[ip]
        else:  # cache it
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except Exception as ex:
                # use whois to resolve this
                print ex.message
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

    def update_traffic_counter_old(self):
        self.metric_prev = copy.deepcopy(self.metric_curr)

    def notify_stats(self):
        # todo report the stats over time since the last interval
        # elapsed time
        """
        if self.traffic_counter["epoch"] == self.traffic_counter_old["epoch"]:
            print self.traffic_counter_old['idx'], self.traffic_counter['idx'],
            (self.traffic_counter["epoch"] - self.traffic_counter_old["epoch"])
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
        """

        # just get the increment of each notify
        data_up_size_rate = (self.metric_curr["data_up"]["size"] - self.metric_prev["data_up"]["size"])
        data_down_size_rate = (self.metric_curr["data_down"]["size"] - self.metric_prev["data_down"]["size"])

        # meta data rate
        meta_up_size_rate = (self.metric_curr["meta_up"]["size"] - self.metric_prev["meta_up"]["size"])
        meta_down_size_rate = (self.metric_curr["meta_down"]["size"] - self.metric_prev["meta_down"]["size"])

        # PACKET
        data_up_c_rate = (self.metric_curr["data_up"]["c"] - self.metric_prev["data_up"]["c"])
        data_down_c_rate = (self.metric_curr["data_down"]["c"] - self.metric_prev["data_down"]["c"])
        meta_up_c_rate = (self.metric_curr["meta_up"]["c"] - self.metric_prev["meta_up"]["c"])
        meta_down_c_rate = (self.metric_curr["meta_down"]["c"] - self.metric_prev["meta_down"]["c"])

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
            }, "time": self.metric_curr["epoch"]            # create timestamp
        }
        # self.traffic_counter_old = self.traffic_counter[:]
        self.update_traffic_counter_old()
        return stats

    @staticmethod
    def is_root():
        try:
            if os.getuid() == 0:
                print("r00thless!!! ")
            else:
                print("Cannot run as a mortal. ")
                # todo: >
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

    @staticmethod
    def get_epoch_ms():
        return int(time.time()) * 1000

    @staticmethod
    def get_time():
        return strftime("%Y-%m-%d %H:%M:%S", gmtime())











