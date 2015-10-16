(function () {
    var jsonDesc;
    // var demoURL = 'https://ast03:8443/render?target=benchbox.ast04.StackSync.cpu_usage&format=json'
    var demoURLCpuUsage = 'https://ast03:8443/render?from=-20minutes&until=now&target=benchbox.*.StackSync.cpu_usage&_uniq=0.24690097919665277&title=benchbox.d119.eth0.bytes_recv&format=json'
    var demoURLRamUsage = 'https://ast03:8443/render?from=-20minutes&until=now&target=benchbox.*.StackSync.memory_usage&_uniq=0.24690097919665277&title=benchbox.d119.eth0.bytes_recv&format=json'
    var demoURLHddUsage = 'https://ast03:8443/render?from=-20minutes&until=now&target=benchbox.*.stacksync_folder.disk_usage&_uniq=0.24690097919665277&title=benchbox.d119.eth0.bytes_recv&format=json'
    var demoURL = 'https://ast03:8443/render?target=collectd.graphite.processes.fork_rate&format=json';
    // demoURLCpuUsage = demoURLHddUsage = demoURLRamUsage = demoURL;
    jsonDesc = {

        /*
        "Total Notifications": {
            source: demoURLCpuUsage,
            GaugeLabel: {
                parent: "#hero-one",
                observer: function (data) {
                    console.log("Label observing " + data);
                },
                title: "Notifications Served",
                type: "max"
            }
        },
        "Poll Time": {
            source: demoURLCpuUsage,
            GaugeGadget: {
                parent: "#hero-two",
                title: "P1",
                observer: function (data) {
                    console.log("Gadget observing " + data);
                }
            }
        },
        */
        /*

         "Total Installs": {
         source: demoURL,
         GaugeLabel: {
         parent: "#hero-three",
         title: "Clients Installed"
         }
         },
         "Clients 1": {
         source: demoURL,
         GaugeGadget: {
         parent: "#hero-three",
         title: "Cl1"
         }
         },
         */
        /*
         "New Message": {
         source: demoURL,
         TimeSeries: {
         parent: '#g1-1',
         title: 'New Message',
         label_offset: 200,
         label_columns: 2,
         time_span_mins: 12,
         observer: function (data) {
         console.log("Time series observing ", data);
         }
         }
         },
         */
        "Ram Usage": {
            source: demoURLRamUsage,
            TimeSeries: {
                title: 'Ram Usage',
                warn: 600,
                error: 800,
                parent: '#g3'
            }
        },

        "Cpu Usage": {
            source: demoURLCpuUsage,
            TimeSeries: {
                title: 'Cpu Usage',
                parent: '#g2'
            }
        },
        "Hdd Usage": {
            source: demoURLHddUsage,
            TimeSeries: {
                title: 'Hdd Usage',
                parent: '#g1'
            }
        }

    };


    var g = new Graphene;
    // g.demo();
    g.build(jsonDesc);


    /*
     var g = new Graphene;
     g.discover('https://10.30.103.95:8443', 'benchbox',
     function (i, url) {
     return  '#g2-3'
     },
     function (description) {
     g.build(description);
     console.log(description)

     })
     */

}).call(this);