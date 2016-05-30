# This has to be a separate type to enable collecting
Puppet::Type.newtype(:mysql_grant) do
  @doc = "Manage a MySQL user's rights."
  ensurable

  autorequire(:file) { '/root/.my.cnf' }

  def initialize(*args)
    super
    # Forcibly munge any privilege with 'ALL' in the array to exist of just
    # 'ALL'.  This can't be done in the munge in the property as that iterates
    # over the array and there's no way to replace the entire array before it's
    # returned to the provider.
    if self[:ensure] == :present and Array(self[:privileges]).count > 1 and self[:privileges].to_s.include?('ALL')
      self[:privileges] = 'ALL'
    end
    # Sort the privileges array in order to ensure the comparision in the provider
    # self.instances method match.  Otherwise this causes it to keep resetting the
    # privileges.
    self[:privileges] = Array(self[:privileges]).map{ |priv|
       # split and sort the column_privileges in the parentheses and rejoin
       if priv.include?('(')
         type, col=priv.strip.split(/\s+|\b/,2)
         type.upcase + " (" + col.slice(1...-1).strip.split(/\s*,\s*/).sort.join(', ') + ")"
       else
         priv.strip.upcase
       end
     }.uniq.reject{|k| k == 'GRANT' or k == 'GRANT OPTION'}.sort!
  end

  validate do
    fail('privileges parameter is required.') if self[:ensure] == :present and self[:privileges].nil?
    fail('table parameter is required.') if self[:ensure] == :present and self[:table].nil?
    fail('user parameter is required.') if self[:ensure] == :present and self[:user].nil?
    fail('name must match user and table parameters') if self[:name] != "#{self[:user]}/#{self[:table]}"
  end

  newparam(:name, :namevar => true) do
    desc 'Name to describe the grant.'

    munge do |value|
      value.delete("'")
    end
  end

  newproperty(:privileges, :array_matching => :all) do
    desc 'Privileges for user'
  end

  newproperty(:table) do
    desc 'Table to apply privileges to.'

    munge do |value|
      value.delete("`")
    end

    newvalues(/.*\..*/,/@/)
  end

  newproperty(:user) do
    desc 'User to operate on.'
    validate do |value|
      # http://dev.mysql.com/doc/refman/5.5/en/identifiers.html
      # If at least one special char is used, string must be quoted

      # http://stackoverflow.com/questions/8055727/negating-a-backreference-in-regular-expressions/8057827#8057827
      if matches = /^(['`"])((?!\1).)*\1@([\w%\.:\-]+)/.match(value)
        user_part = matches[2]
        host_part = matches[3]
      elsif matches = /^([0-9a-zA-Z$_]*)@([\w%\.:\-]+)/.match(value)
        user_part = matches[1]
        host_part = matches[2]
      elsif matches = /^(?:(?!['`"]).*)([^0-9a-zA-Z$_]).*@.+$/.match(value)
        # does not start with a quote, but contains a special character
        raise(ArgumentError, "Database user #{value} must be properly quoted, invalid character: '#{matches[1]}'")
      else
        raise(ArgumentError, "Invalid database user #{value}")
      end

      raise(ArgumentError, 'MySQL usernames are limited to a maximum of 16 characters') unless user_part.size <= 16
    end
  end

  newproperty(:options, :array_matching => :all) do
    desc 'Options to grant.'
  end

end
