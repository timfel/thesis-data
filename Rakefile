require "open3"

module Enumerable
  def sum
    self.inject(0){|accum, i| accum + i }
  end

  def mean
    self.sum/self.length.to_f
  end

  def sample_variance
    m = self.mean
    sum = self.inject(0){|accum, i| accum +(i-m)**2 }
    sum/(self.length - 1).to_f
  end

  def standard_deviation
    return Math.sqrt(self.sample_variance)
  end
end

class String
  def go(arg)
    "#{self} #{arg}"
  end
end

class Proc
  def go(arg)
    self.call arg
  end
end

Server = fork do
  require "webrick"
  s = WEBrick::HTTPServer.new(:Port => 9001, :DocumentRoot => Dir.pwd)
  trap('INT') { s.shutdown; exit }
  s.start
end

ldpath = File.expand_path("../repositories/babelsberg-r/dependencies/z3/build", __FILE__)
Impls = {
  "rb" => "env LD_LIBRARY_PATH=#{ldpath} repositories/babelsberg-r/bin/topaz",
  "st" => Proc.new { |arg| "squeak x86_64 runners/BabelsbergS.image ../#{arg}" },
  "js" => "nodejs runners/babelsberg-js-benchmarks.js",
  "chromejs" => Proc.new do |arg|
    "chromium-browser --temp-profile --enable-logging=stderr --v=1  http://localhost:9001/runners/babelsbergjs.bench.html?file=../#{arg.gsub('chromejs', 'js')}"
  end
}

KaplanRunner = Proc.new do |arg|
  file = File.basename(arg)
  main = File.basename(arg, ".kaplan").capitalize
  cp = "-classpath .:jars/z3.jar"\
       ":jars/purescala-definitions_2.9.0-1-1.0.jar"\
       ":jars/constraint-programming-plugin_2.9.0-1-1.0.jar"\
       ":jars/funcheck_2.9.0-1-1.0.jar"\
       ":jars/funcheck-plugin_2.9.0-1-1.0.jar"\
       ":scala/lib/scala-compiler.jar"\
       ":scala/lib/scala-library.jar".gsub(":", ":repositories/kaplan/")
  puts "repositories/kaplan/scalac-kaplan #{cp} #{arg}"
  system "repositories/kaplan/scalac-kaplan #{cp} #{arg}"
  "repositories/kaplan/scala-kaplan #{main}"
end

TurtleRunner = Proc.new do |arg|
  exe = arg.split('.')[0...-1].join(".")
  "repositories/turtle/turtle/turtle -Lrepositories/turtle/libturtle/.libs -OCJGD6 -Irepositories/turtle -p repositories/turtle/crawl -m #{exe} #{arg} && \
   env LD_LIBRARY_PATH=repositories/turtle/libturtle/.libs #{exe}"
end

Langs = {
  "kaplan" => KaplanRunner,
  "turtle" => TurtleRunner,
  "prolog" => "prolog -t 'bench(10).'"
}.merge(Impls)

%w[read-access write-access edit].each do |n|
  namespace n do
    Impls.each_pair do |name, cmd|
      if File.exist? "benchmark-#{n}/benchmark.#{name}"
        desc "Run #{n} on #{name}"
        task name do
          cmdline = cmd.go("benchmark-#{n}/benchmark.#{name}")
          puts cmdline
          system cmdline
        end
      else
        task name do; end
      end
    end
    desc "Run #{n} on all"
    task :all => Impls.keys do
    end
  end
end

desc "Run JIT benchmarks"
task :jit do
  system "nodejs benchmark-jit/babelsberg-js-benchmarks.js"
end

namespace :compare do
  languages = benchmarks = nil
  benchmarks = %w[animals layout sendmoremoney].map do |benchmark|
    namespace benchmark do
      languages = %w[rb chromejs prolog kaplan turtle st].map do |lang|
        desc "Run cross-language benchmark #{benchmark} on #{lang}"
        task lang do
          cmdline = Langs[lang].go("benchmark-constraint-languages/#{benchmark}.#{lang}")
          puts cmdline
          system cmdline
        end
        lang
      end
      desc "Run all comparisons for #{benchmark}"
      task :all, [:language] do |t, args|
        args = [args[:language]].compact
        args = languages if args.empty?
        MAGIC = /THIS IS THE TIME:\s*(\d+\.?\d*)/
        results = args.map do |t|
          [t, 10.times.map do
             stdout, stderr, status = Open3.capture3("timeout -k 10 600 rake compare:#{benchmark}:#{t}")
             print stdout, stderr
             numbers = (stdout + stderr).scan(MAGIC)
             numbers.flatten.map(&:to_f)
           end].flatten
        end
        results.each do |r|
          lang = r[0]; numbers = r[1..-1]
          File.open('compare-results.txt', 'w') { |f| f << "#{r}\n" }
          puts "\n\n\t#{benchmark}.#{lang}: #{numbers.mean}, #{numbers.sample_variance}, #{numbers.standard_deviation}\n\n"
        end
      end
    end
    benchmark
  end
  desc "Run all comparison benchmarks"
  task :all do
    benchmarks.each { |ea| Rake::Task["compare:#{ea}:all"].invoke }
  end
end

at_exit { Process.kill 2, Server }
