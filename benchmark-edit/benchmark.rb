$LOAD_PATH.unshift(File.expand_path("../../runners/", __FILE__))
require "mybenchmark"
require "libcassowary"

class Mercury
  def initialize
    @top = 10
    @bottom = 0
  end

  def top=(num)
    @top = num
  end

  def top
    @top
  end

  def bottom
    @bottom
  end

  def height
    @top - @bottom
  end

  def inspect
    "<Mercury: #{@top}->#{@bottom}>"
  end
end

class Mouse
  def initialize
    @location_y = 10
  end

  def location_y
    @location_y
  end

  def location_y=(arg)
    @location_y = arg
  end

  def inspect
    "<Mouse: #{@location_y}>"
  end
end

class Rectangle
  def initialize(name, top, bottom)
    @name = name
    @top = top
    @bottom = bottom
  end

  def top
    @top
  end

  def top=(arg)
    @top = arg
  end

  def bottom
    @bottom
  end

  def bottom=(arg)
    @bottom = arg
  end

  def inspect
    "<#{@name} Rectangle: #{@top}->#{@bottom}>"
  end
end

class Thermometer < Rectangle
  def initialize(top, bottom)
    super("thermometer", top, bottom)
  end

  def inspect
    "<Thermometer: #{@top}->#{@bottom}>"
  end
end

class Display
  def initialize
    @number = 0
  end

  def number
    @number
  end

  def number=(arg)
    @number = arg
  end

  def inspect
    "<Display: #{@number}>"
  end
end

mouse = mercury = thermometer = grey = white = temperature = display = nil

Resetter = Proc.new do |label|
  if label.start_with? "Imperative"
    mouse = Mouse.new
    mercury = Mercury.new
    thermometer = Thermometer.new(200, 0)
    grey = Rectangle.new("grey", mercury.top, mercury.bottom)
    white = Rectangle.new("white", thermometer.top, mercury.top)
    temperature = mercury.height
    display = Display.new
  end
  if label.start_with? "Declarative" or label.start_with? "Edit"
    mouse = Mouse.new
    mercury = Mercury.new
    thermometer = Thermometer.new(200, 0)
    grey = Rectangle.new("grey", mercury.top, mercury.bottom)
    white = Rectangle.new("white", thermometer.top, mercury.top)
    temperature = mercury.height
    display = Display.new

    always { temperature == mercury.height }
    always { white.top == thermometer.top }
    always { white.bottom == mercury.top }
    always { grey.top == mercury.top }
    always { grey.bottom == mercury.bottom }
    always { display.number == temperature }
    always { mercury.top == mouse.location_y }
    always { mercury.top <= thermometer.top }
    always { mercury.bottom == thermometer.bottom }
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

Benchmark.ips do |x|
  x.config(:suite => suite)
  x.report('Imperative Drag Simulation') do |t|
    t.times do
      100.times do |i|
        mouse.location_y = i
        old = mercury.top
        mercury.top = mouse.location_y
        if mercury.top > thermometer.top
          mercury.top = thermometer.top
        end
        temperature = mercury.top
        if (old < mercury.top)
          # moves upwards (draws over the white)
          grey.top = mercury.top
        else
          # moves downwards (draws over the grey)
          white.bottom = mercury.top
        end
        display.number = temperature
      end
    end
  end
  x.report('Declarative Drag Simulation') do |t|
    t.times { 100.times { |i| mouse.location_y = i } }
  end
  x.report('Edit Drag Simulation') do |t|
    t.times do
      edit(stream: 100.times.each, accessors: []) { mouse.location_y }
    end
  end
  x.compare!
end
