class benchbox{


  /*
   compilar impressions
  */


  /*
  file{
    '/home/vagrant/profile.csv':
      recurse => true,
      ensure => present,
      content=> $facter
  }
  */

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
  exec {
    'compile_impressions':
      command => 'make && mv impressions ../impressions',
      path    => ['/usr/bin/', '/bin/'],
      cwd     => '/home/vagrant/workload_generator/external/impressions-code',
      onlyif  => '[ ! -e "/usr/bin/stacksync" ]'
  }


}
