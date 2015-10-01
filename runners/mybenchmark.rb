$LOAD_PATH.unshift(File.expand_path("../../runners/benchmark-ips/lib/", __FILE__))
require "benchmark/ips"

module GC
  def self.start
  end
end

class IO
  attr_accessor :sync

  def printf(format_string, *args)
    self << (format_string.%(args))
  end
end

class String
  def gsub!(*args, &block)
    self.replace(self.gsub(*args, &block))
  end
end

class Time
  def +(numeric)
    self - -numeric
  end

  def <=>(other)
    self.to_i <=> other
  end
end

class String
  alias_method :orig_mod, :"%"
  def %(*args)
    newself = self.gsub("%\.", "%0.").gsub(/%\d+(\.\d+)?/, "%").gsub("%%", "pc")
    # puts "Formatting me: '#{self}', replaced as '#{newself}'"
    newself.orig_mod(*args)
  end
end

module Kernel
  def caller(*args)
    ["Fake Caller"]
  end
end
