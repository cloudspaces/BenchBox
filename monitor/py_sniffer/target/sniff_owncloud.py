from sniff import Sniff
from threading import Thread

class OwnCloud(Sniff):

    def __init__(self, args):

        super(self.__class__, self).__init__(args)
        self.whoami = (self).__class__.__name__
        print self.whoami
        self.capture_filter_ips = [self.my_ip, self.sync_server_ip]
        self.capture_filter_ports = [8080]

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
