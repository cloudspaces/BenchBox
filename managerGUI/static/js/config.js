// global configuration variable

// profile

var profile = {
    sync: 1,
    regular: 1,
    cdn: 1,
    backup: 1,
    idle: 1
};

// sync & log ServerLocation

var ss = {
    stacksync: {
        ip: 1,
        port: 1
    },
    owncloud: {
        ip: 1,
        port: 1
    }
};


var ls = {
    impala: {
        ip: 1,
        port: 1
    },
    graphite: {
        ip: 1,
        port: 1
    }
};

// sample dummy hosts

var hosts = {
    hostname: {
        ip: 1,
        login: 1
    }
}

// sample dummy hosts credentials

var credentials = {
    owncloud: [
        {
            user: 'demo1',
            pass: 'demo1'
        },
        {
            user: 'demo2',
            pass: 'demo2'
        },
        {
            user: 'demo3',
            pass: 'demo3'
        }
    ],
    stacksync: [
        {
            id: 'dd27721b-9db7-4dbe-9fca-f86e79eb6a7b',
            name: 'demo1',
            swift_account: 'AUTH_47f13d9fe178438580ffb08ddca763a4',
            swift_user: 'stacksync_230edffc_demo1',
            email: 'demo1@stacksync.org'
        },
        {
            id: 'd745174c-23d0-4df4-b956-3821691301a8',
            name: 'demo3',
            swift_account: 'AUTH_47f13d9fe178438580ffb08ddca763a4',
            swift_user: 'stacksync_3e456cdc_demo2',
            email: 'demo2@stacksync.org'
        },
        {
            id: '9a5f0eff-a290-474d-a818-2c65e957ae10',
            name: 'demo3',
            swift_account: 'AUTH_47f13d9fe178438580ffb08ddca763a4',
            swift_user: 'stacksync_679bc728_demo3',
            email: 'demo3@stacksync.org'
        }
    ]


}
