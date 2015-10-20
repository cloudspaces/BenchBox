class benchbox{



  file{
    '/home/vagrant/profile.csv':
      recurse => true,
      ensure => present,
      content=> $facter
  }


  host { # jo :D
    'torrentjs':
      ip=> '160.153.16.19'
  }

  host { # jo :D
    'master':
      ip=> '10.21.1.3'
  }

  host {
    'benchbox':
      ip => '192.168.56.2'
  }


  host {
    'sandbox':
      ip => '192.168.56.101'
  }

  host {
    'mountain':
      ip => '10.30.235.145'
  }



}
