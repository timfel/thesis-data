$LOAD_PATH.unshift(File.expand_path("../../runners/", __FILE__))
require "mybenchmark"
require "libcassowary"

class MockObject
  attr_accessor :a, :b, :c, :d, :e

  def initialize
    @a,@b,@c,@d,@e = 1,1,1,1,1
  end
end

obj, constraint = nil, nil

Resetter = Proc.new do |label|
  obj = MockObject.new
  if label.start_with? "Constrained"
    constraint.disable if constraint
    constraint = always do
      obj.a == 1 &&
        obj.b == 1 &&
        obj.c == 1 &&
        obj.d == 1 &&
        obj.e == 1
    end
    constraint.disable if label.end_with? "(disabled)"
  end
end

class SetupSuite
  def warming(label, *args)
    Resetter[label]
  end
  def warmup_stats(*); end
  alias_method :add_report, :warmup_stats
  alias_method :running, :warming
end
suite = SetupSuite.new

benchmark = Proc.new { |t| t.times { obj.a + obj.b + obj.c + obj.d + obj.e } }

Benchmark.ips do |x|
  x.config(:suite => suite)
  x.report('Unconstrained Read', &benchmark)
  x.report('Constrained Read', &benchmark)
  x.report('Constrained Read (disabled)', &benchmark)
  x.compare!
end
