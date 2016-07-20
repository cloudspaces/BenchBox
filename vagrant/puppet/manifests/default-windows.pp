# this puppet deploys a client with all the software dependencies - only stacksync

# -------------------------------------------------------------------------------------------------------
# sandBox
# -------------------------------------------------------------------------------------------------------
node 'sandBox' {
  file {
    ['/Users/vagrant/stacksync_folder',
      '/Users/vagrant/.stacksync',
      '/Users/vagrant/.stacksync/cache',
      '/Users/vagrant/dropbox_folder',
      '/Users/vagrant/box_folder',
      '/Users/vagrant/drive_folder',
      '/Users/vagrant/one_folder',
      '/Users/vagrant/sugar_folder'
    ]:
      ensure  => directory,
      owner   => vagrant,
      group   => vagrant,
      mode    => '0644',
      recurse => true
  } ->
  exec {
    'run messagequeue boostrap sandBox status':
      command => 'startPeerConsumer.dat',
      user    => 'vagrant',
      group   => 'vagrant',
      cwd     => '/vagrant'
  }

}


# -------------------------------------------------------------------------------------------------------
# benchBox
# -------------------------------------------------------------------------------------------------------
node 'benchBox' {
  class { 'apt':
    update => {
      frequency => 'daily',
    },
  }->
  class {
    'benchbox':
  }

  exec {
    'run message queue boostrap benchBox status':
      command => 'nohup ./startPeerConsumer.sh & ',
      user    => 'vagrant',
      group   => 'vagrant',
      cwd     => '/home/vagrant/vagrant',
      path    => ['/usr/bin', '/bin/']
  }

  # file{
  #    '/home/vagrant/application.properties':
  #    ensure => file,
  #    source => 'puppet:///files/application.properties'
  # }


}

node 'win7-vagrant' {

  file {
    [
      '/Users/vagrant/stacksync_folder',
      '/Users/vagrant/.stacksync',
      '/Users/vagrant/.stacksync/cache',
      '/Users/vagrant/dropbox_folder',
      '/Users/vagrant/box_folder',
      '/Users/vagrant/drive_folder',
      '/Users/vagrant/one_folder',
      '/Users/vagrant/sugar_folder'
    ]:
      ensure  => directory,
      owner   => vagrant,
      group   => vagrant,
      mode    => '0644',
      recurse => true
  } ->
  /*
  exec {
    'run dropbox client setup':
      command => "nohup /vagrant/scripts/config.dropbox.sh &",
      user    => 'vagrant',
      group   => 'vagrant',
      cwd     => '/vagrant',
      path    => ['/usr/bin','/bin/']
  }

  ->
  */
  exec {
    'run messagequeue boostrap sandBox status':
      command => 'startPeerConsumer.dat',
      user    => 'vagrant',
      group   => 'vagrant',
      cwd     => '/vagrant'
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

