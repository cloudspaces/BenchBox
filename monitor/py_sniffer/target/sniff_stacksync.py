from sniff import Sniff
from threading import Thread

class StackSync(Sniff):
    def __init__(self, args):
        super(self.__class__, self).__init__(args)
        self.whoami = (self).__class__.__name__
        self.capture_filter_ips = [self.my_ip, self.sync_server_ip]
        self.capture_filter_ports = [self.sync_server_port, "5000", "8080"]

        self.live_capture.setfilter(
            "(port " + " || port ".join(self.capture_filter_ports) + ") && (host " + " && host ".join(self.capture_filter_ips) + ")",  # filter
        )
        print self.whoami

    def capture(self):
        self.capture_thread = Thread(target=self.live_capture.loop, args=[self.packet_limit, self.__on_recv_pkts])
        self.capture_thread.start()
        return self.capture_thread

    def capture_quit(self):
        # print "try terminate"
        # self.capture_thread.terminate()
        self.capture_thread.join(timeout=1)
        # print "try kill"

        # self.capture_thread.kill()



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

        # print "is stacksync"
        flow = None
        if src_ip == self.my_ip:
            self.metric_curr["total_up"]["size"] += total_size
            self.metric_curr["total_up"]["c"] += 1
            flow = "up"
        elif dst_ip == self.my_ip:
            self.metric_curr["total_up"]["size"] += total_size
            self.metric_curr["total_up"]["c"] += 1
            flow = "down"

        if flow is None:  #
            return flow

        # print flow

        if flow == "down":
            if src_port == 8080:
                # print "Data download {}".format(data_size)
                self.metric_curr["data_down"]["size"] += total_size
                self.metric_curr["data_down"]["c"] += 1
            elif src_port == 5672:
                # print "Meta down {}".format(data_size)
                self.metric_curr["meta_down"]["size"] += total_size
                self.metric_curr["meta_down"]["c"] += 1
        else:
            if dst_port == 8080:
                # print "Data upload {}".format(data_size)
                self.metric_curr["data_up"]["size"] += total_size
                self.metric_curr["data_up"]["c"] += 1
            elif dst_port == 5672:
                # print "Meta upload {}".format(data_size)
                self.metric_curr["meta_up"]["size"] += total_size
                self.metric_curr["meta_up"]["c"] += 1
 
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
