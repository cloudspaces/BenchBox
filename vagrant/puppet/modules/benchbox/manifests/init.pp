class benchbox{


  /*
   compilar impressions
  */


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
      ip => '10.30.236.141'
  }

  exec {
    'compile_impressions':
      command => 'make && mv impressions ../impressions',
      path    => ['/usr/bin/', '/bin/'],
      cwd     => '/home/vagrant/workload_generator/external/impressions-code',
      # onlyif  => '[ ! -e "/usr/bin/stacksync" ]'
      onlyif  => '[ ! -e "/home/vagrant/workload_generator/external/impressions" ]'
  }


}
