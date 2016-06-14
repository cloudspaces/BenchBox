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


  # dropbox
  /*
    class {'dropbox::config':
    user =>  'benchbox@outlook.com',
    password => 'salou2010'
  }

  include dropbox
  */

}

