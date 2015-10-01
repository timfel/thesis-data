$LOAD_PATH.unshift(File.expand_path("../../runners/", __FILE__))
require "mybenchmark"
require "libcassowary"

class MockObject
  attr_accessor :a, :b, :c, :d, :e

  def initialize(a=1,b=1,c=1,d=1,e=1)
    @a,@b,@c,@d,@e = a,b,c,d,e
  end
end

obj, constraint = nil, nil

Resetter = Proc.new do |label|
  obj = MockObject.new
  if label.start_with? "Constrained"
    constraint.disable if constraint
    constraint = always do
      obj.a >= 1 &&
        obj.b >= 1 &&
        obj.c >= 1 &&
        obj.d >= 1 &&
        obj.e >= 1
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

benchmark = Proc.new { |t| t.times { obj.a += 1; obj.b += 1; obj.c += 1; obj.d += 1; obj.e += 1 } }

Benchmark.ips do |x|
  x.config(:suite => suite)
  x.report('Unconstrained Write', &benchmark)
  x.report('Constrained Write', &benchmark)
  x.report('Constrained Write (disabled)', &benchmark)
  x.report('Constrained Write (edit)') do |times|
    class MyStream
      def initialize(times)
        @times = times
      end
      def next
        raise StopIteration if @times == 0
        o = MockObject.new(@times, @times, @times, @times, @times)
        @times -= 1
        o
      end
    end
    edit(stream: MyStream.new(times), accessors: ["a", "b", "c", "d", "e"]) { obj }
  end
  x.compare!
end
