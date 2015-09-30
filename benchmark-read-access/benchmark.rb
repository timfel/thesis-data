require 'benchmark'

module GC
  def self.start
  end
end

class IO
  attr_accessor :sync
end

class String
  def gsub!(*args, &block)
    self.replace(self.gsub(*args, &block))
  end
end

class Benchmark::Tms
  def format(format = nil, *args)
    return "#{utime}\t#{stime}\t#{total}\t#{real}\n"
  end
end

require "libcassowary"

class MockObject
  attr_accessor :a, :b, :c, :d, :e

  def initialize
    @a,@b,@c,@d,@e = 1,1,1,1,1
  end
end

Iterations = 1000
sumObj = MockObject.new
obj = MockObject.new

constraint = always do
  obj.a == 1 &&
    obj.b == 1 &&
    obj.c == 1 &&
    obj.d == 1 &&
    obj.e == 1
end

Benchmark.bmbm do |x|
  x.report('Unconstrained Read') { Iterations.times { sumObj.a + sumObj.b + sumObj.c + sumObj.d + sumObj.e } }
  x.report('Constrained Read') { Iterations.times { obj.a + obj.b +
        obj.c + obj.d + obj.e
  } }
  x.report('Constrained Read (disabled)') {
    constraint.disable
    Iterations.times {
    obj.a + obj.b +
      obj.c + obj.d + obj.e
  } }
end
