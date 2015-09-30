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

Iterations = 100000
sumObj = MockObject.new
obj = MockObject.new

constraint = always do
  obj.a >= 1 &&
    obj.b >= 1 &&
    obj.c >= 1 &&
    obj.d >= 1 &&
    obj.e >= 1
end

Benchmark.bmbm do |x|
  x.report('Unconstrained Write') do
    Iterations.times { sumObj.a += sumObj.b += sumObj.c += sumObj.d += sumObj.e += 1 }
  end
  x.report('Constrained Write') do
    Iterations.times { obj.a += obj.b += obj.c += obj.d += obj.e += 1 }
  end
  # x.report('Constrained Write (edit)') do
  #   edit(Iterations.times.each) { obj.a }
  #   edit(Iterations.times.each) { obj.b }
  #   edit(Iterations.times.each) { obj.c }
  #   edit(Iterations.times.each) { obj.d }
  #   edit(Iterations.times.each) { obj.e }
  # end
  x.report('Constrained Write (disabled)') do
    constraint.disable
    Iterations.times { obj.a += obj.b += obj.c += obj.d += obj.e + 1 }
  end
end
