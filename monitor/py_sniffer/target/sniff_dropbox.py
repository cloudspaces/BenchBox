from sniff import Sniff
from threading import Thread

class Dropbox(Sniff):

    def __init__(self, args):
        super(self.__class__, self).__init__(args)
        self.whoami = (self).__class__.__name__
        print self.whoami
        self.capture_filter_ips = [self.my_ip]
        self.capture_filter_ports = ["443"]

        self.live_capture.setfilter(
         "(port " + " || port ".join(self.capture_filter_ports) + ") && (host " + " && host ".join(self.capture_filter_ips) + ")",  # filter
        )

    def capture(self):
        self.capture_thread = Thread(target=self.live_capture.loop, args=[self.packet_limit, self.__on_recv_pkts])
        self.capture_thread.start()
        return self.capture_thread

    def capture_quit(self):
        Thread.join(self.capture_thread, timeout=1)

    def hello(self):
        print "{} say hello".format(self.whoami)

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

        self.add_flow(src_host, dst_host, ether_packet.get_size())

        # TCP OR UDP
        packet_protocol = packet_type.child()
        packet_protocol_type = packet_protocol.__class__.__name__
        src_port = 0
        dst_port = 0
        data_size = packet_protocol.get_size()
        if packet_protocol.protocol == 17:
            # this is UDP
            src_port = packet_protocol.get_uh_sport()
            dst_port = packet_protocol.get_uh_dport()
        elif packet_protocol.protocol == 6:
            # this maybe TCP
            src_port = packet_protocol.get_th_sport()
            dst_port = packet_protocol.get_th_dport()
        elif packet_protocol.protocol == 1:
            # this is ICMP (Internet Controll Message)
            return None
        elif packet_protocol.protocol is None:
            return None
        else:
            raise NotImplemented

        self.packet_index += 1



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
            self.metric_curr["total_up"]["size"] += total_size
            self.metric_curr["total_up"]["c"] += 1
        elif src_port == 443:
            self.metric_curr["total_down"]["size"] += total_size
            self.metric_curr["total_down"]["c"] += 1
            flow = "down"

        if flow is None:  # else: unknown flow
            return flow

        # print "the flow is: {}".format(flow)
        # data goes through
        if flow == "down":
            if "d.v.dropbox.com" in src_host:
                self.metric_curr["meta_down"]["size"] += total_size
                self.metric_curr["meta_down"]["c"] += 1
            elif "cloudfront" in src_host:
                # im download from server == data down
                self.metric_curr["data_down"]["size"] += total_size
                self.metric_curr["data_down"]["c"] += 1
            elif "dropbox" in src_host:
                self.metric_curr["meta_down"]["size"] += total_size
                self.metric_curr["meta_down"]["c"] += 1
            elif "amazonaws" in src_host:
                self.metric_curr["data_down"]["size"] += total_size
                self.metric_curr["data_down"]["c"] += 1
            else:
                # use whois to resole this
                self.metric_curr["misc_down"]["size"] += total_size
                self.metric_curr["misc_down"]["c"] += 1
        # elif flow == "up":
        else:

            if "d.v.dropbox.com" in dst_host:
                self.metric_curr["meta_up"]["size"] += total_size
                self.metric_curr["meta_up"]["c"] += 1
            elif "cloudfront" in dst_host:
                # im download from server == data down
                self.metric_curr["data_up"]["size"] += total_size
                self.metric_curr["data_up"]["c"] += 1
            elif "dropbox" in dst_host:
                self.metric_curr["meta_up"]["size"] += total_size
                self.metric_curr["meta_up"]["c"] += 1
            elif "amazonaws" in dst_host:
                self.metric_curr["data_up"]["size"] += total_size
                self.metric_curr["data_up"]["c"] += 1
            else:
                # use whois to resolve this ip's # aqui no entrara nunca ni referenciando por ip
                self.metric_curr["misc_up"]["size"] += total_size
                self.metric_curr["misc_up"]["c"] += 1

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

        self.metric_curr['epoch'] = self.get_epoch_ms()
        self.metric_curr['idx'] = self.packet_index
