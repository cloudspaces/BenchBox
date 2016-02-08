class dropbox::package {
  Exec {
    path   => '/bin:/sbin:/usr/bin:/usr/sbin',
  }

  $download_arch = $::architecture ? {
    'i386'   => 'x86',
    'x86_64' => 'x86_64',
    'amd64'  => 'x86_64',
  }

  user { $dropbox::config::dx_uid:
    ensure     => present,
    gid        => $dropbox::config::dx_gid,
    managehome => true,
    system     => true,
    home       => $dropbox::config::dx_home,
    comment    => 'Dropbox Service Account',
  }
  group { $dropbox::config::dx_gid:
    ensure => present,
    system => true
  }

  exec { 'download-dropbox-cli':
    command => "wget -O /tmp/dropbox.py \"https://www.dropbox.com/download?dl=packages/dropbox.py\"",
    unless  => 'test -f /tmp/dropbox.py',
    require => User[$dropbox::config::dx_uid],
  }
  file { '/usr/local/bin/dropbox':
    source  => '/tmp/dropbox.py',
    mode    => 755,
    require => Exec['download-dropbox-cli']
  }


  exec { 'download-dropbox':
    command => "wget -O /tmp/dropbox.tar.gz \"http://www.dropbox.com/download/?plat=lnx.${download_arch}\"",
    unless => "test -d ~${dropbox::config::dx_uid}/.dropbox-dist",
    require => User[$dropbox::config::dx_uid],
  }
  exec { 'install-dropbox':
    command => "tar -zxvf /tmp/dropbox.tar.gz -C ~${dropbox::config::dx_uid}",
    unless => "test -d ~${dropbox::config::dx_uid}/.dropbox-dist",
    require => Exec['download-dropbox'],
  }
  file { '/tmp/dropbox.tar.gz':
    ensure  => 'absent',
    require => Exec['install-dropbox'],
  }

  file { '/etc/init.d/dropbox':
    source => "puppet:///modules/dropbox/etc/init.d/dropbox.${::operatingsystem}",
    owner  => root,
    group  => root,
    mode   => 755,
  }
}
