# this puppet deploys a client with all the software dependencies - only stacksync

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
    'git':
  }->
  class {
    'java':
      distribution => 'jdk',
  }->
  class { 'python' :
    version    => 'system',
    pip        => true,
    dev        => true,
    virtualenv => true
  }->
  package {
    ['numpy']:
      ensure   => 'installed',
      provider => pip
  }->
  package {
    ['termcolor','pika']:
      ensure   => 'installed',
      provider => pip
  }->
  package {
    ['simpy',]:
      ensure   => '2.3',
      provider => pip
  }
  ->
  package {
    'python-scipy':
      ensure   => 'installed',
  }
  ->
  class {
    'benchbox':
  }
  ->
  class {
    'vim':
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
# common
  class { 'apt':
    update => {
      frequency => 'daily',
    },
  }->
  class {
    'git':
  }->
  class { 'python' :
    version    => 'system',
    pip        => true,
    dev        => true,
    virtualenv => true
  }
  ->
  package {
    ['python-setuptools', 'build-essential']:
      ensure => installed
  }
  ->
  # owncloud
  class{
    "owncloud":
      rmq_host => '10.30.232.183'
  }
  ->
  file {
    ['/home/vagrant/owncloud_folder']:
      ensure  => directory,
      owner   => vagrant,
      group   => vagrant,
      mode    => '0644',
      recurse => true
  }
  # stacksync
  ->
  class {
    'java':
      distribution => 'jdk',
  }->
  class {
    'vsftpd':
      write_enable            => 'YES',
      ftpd_banner             => 'SandBox FTP Server',
      anonymous_enable        => 'YES',
      anon_upload_enable      => 'YES',
      anon_mkdir_write_enable => 'YES',
      pasv_min_port           => 10090,
      pasv_max_port           => 10100,
  }->
  file
  {
    ["/etc/vsftpd.user_list" ]:
      recurse => true,
      ensure  => present,
      mode    => 0777,
      content => 'vagrant vagrant'
  }->
  file { "/srv/ftp":
    ensure => "directory",
    owner  => "ftp",
    group  => "ftp",
    mode   => 755,
  }
  ->
  class {
    "stacksync":
      rmq_host                  => '10.30.235.91',
      p_repo_connection_authurl => 'http://10.30.235.91:5000/v2.0/tokens'
  }->
  file {
    ['/home/vagrant/stacksync_folder', '/home/vagrant/.stacksync', '/home/vagrant/.stacksync/cache']:
      ensure  => directory,
      owner   => vagrant,
      group   => vagrant,
      mode    => '0644',
      recurse => true
  }->
  # PIL
  package {
    ['netifaces','psutil']:
      ensure   => 'installed',
      provider => pip,
      require  => Package['python-pip']
  }
  ->  package{
    ['python-pcapy','python-bzrlib','scapy']:
      ensure    => installed
  }
  ->  package {
    ['bitarray','thrift', 'pika','termcolor']:
      ensure   => 'installed',
      provider => pip
  }
  ->
  exec {
    'upagrade pip setup tools with include operation...':
      command => 'sudo pip install -U setuptools',
      user    => 'vagrant',
      group   => 'vagrant',
      path    => ['/usr/bin']
  }
  ->
  package {
    ['impyla']:
      ensure   => 'installed',
      provider => pip
  }
  ->
  package {
    ['dpkt']:
      ensure   => 'installed',
      provider => pip
  }
  ->
  exec {
    "check_presence_of_previous_execution":
      command => 'kill -9 $(head -n 1 /tmp/StackSync.pid)',
      onlyif  => 'test -e /tmp/StackSync.pid',
      user    => 'vagrant',
      group   =>'vagrant',
      path    => ['/usr/bin', '/bin/'],
      returns => [0,1]
  }->
  class{
    "vim":
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

}


