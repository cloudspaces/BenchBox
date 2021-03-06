# this puppet deploys a client with all the software dependencies - only stacksync

# -------------------------------------------------------------------------------------------------------
# benchBox
# -------------------------------------------------------------------------------------------------------
node 'benchBox' {
  # class { 'apt':
  #   update => {
  #     frequency => 'daily',
  #   },
  # }->
  class {
    'benchbox':
  }
  ->
  exec {
    'run message queue boostrap benchBox status':
      command => 'nohup ./startPeerConsumer.sh & ',
      user    => 'vagrant',
      group   => 'vagrant',
      cwd     => '/vagrant',
      path    => ['/usr/bin', '/bin/']
  }

  # file{
  #    '/home/vagrant/application.properties':
  #    ensure => file,
  #    source => 'puppet:///files/application.properties'
  # }


}

define download_file(
  $site="",
  $cwd="",
  $creates="") {

  exec { $name:
    path    => ['/bin','/usr/bin'],
    command => "wget ${site}/${name}",
    cwd     => $cwd,
    creates => "${cwd}/${name}", # if this files does not exist then the it ill not execute...
  }

}






# -------------------------------------------------------------------------------------------------------
# sandBox
# -------------------------------------------------------------------------------------------------------
node 'sandBox' {
  /*
  # owncloud
  class{
    "owncloud":
      rmq_host => '10.30.232.183'
  }
  ->
  # stacksync
  class {
    "stacksync":
      rmq_host                  => '10.30.235.91',
      p_repo_connection_authurl => 'http://10.30.235.91:5000/v2.0/tokens'
  }->
  */


  file {
    ['/home/vagrant/stacksync_folder',
      '/home/vagrant/.stacksync',
      '/home/vagrant/.stacksync/cache',
      '/home/vagrant/dropbox_folder',
      '/home/vagrant/box_folder',
      '/home/vagrant/drive_folder',
      '/home/vagrant/one_folder',
      '/home/vagrant/sugar_folder'
    ]:
      ensure  => directory,
      owner   => vagrant,
      group   => vagrant,
      mode    => '0644',
      recurse => true
  } ->

  exec {
    'run dropbox client setup':
      command => "nohup /vagrant/scripts/config.dropbox.sh &",
      user    => 'vagrant',
      group   => 'vagrant',
      cwd     => '/vagrant',
      path    => ['/usr/bin','/bin/']
  }
  ->
  exec {
    'run messagequeue boostrap sandBox status':
      command => 'nohup ./startPeerConsumer.sh & ',
      user    => 'vagrant',
      group   => 'vagrant',
      cwd     => '/vagrant',
      path    => ['/usr/bin', '/bin/']
  }

  ->

  file { "/home/vagrant/workload_generator/external/impressions":
    mode => 755,
  }
  /*
  exec {
    'give execution permision to impression':
      command => 'chmod u+x ',
      user => 'vagrant',
      group => 'vagrant',
      cwd => '/home/vagrant/workload_generator/external/impressions'
  }
  */

  # dropbox
  /*
    class {'dropbox::config':
    user =>  'benchbox@outlook.com',
    password => 'salou2010'
  }

  include dropbox
  */

}


