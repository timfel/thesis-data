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

ldpath = File.expand_path("../repositories/babelsberg-r/dependencies/z3/build", __FILE__)
Impls = {
  "rb" => "env LD_LIBRARY_PATH=#{ldpath} repositories/babelsberg-r/bin/topaz",
  "st" => Proc.new { |arg| "squeak x86_64 runners/BabelsbergS.image ../#{arg}" },
  "js" => "nodejs runners/babelsberg-js-benchmarks.js"
}

KaplanRunner = Proc.new do |arg|
  puts "KAPLAN NOT WORKING (MISSING OLD 32BIT STUFF)"
  path = arg.split('/')[0...-1].join(".")
  main = arg.split('/').last.capitalize.split('.').first
  "repositories/kaplan/scalac-kaplan #{arg} &&\
   repositories/kaplan/scala-kaplan #{path}.#{main}"
end

TurtleRunner = Proc.new do |arg|
  exe = arg.split('.')[0...-1].join(".")
  "repositories/turtle/turtle/turtle -Lrepositories/turtle/libturtle/.libs -OCJGD6 -Irepositories/turtle -p repositories/turtle/crawl -m #{exe} #{arg} && \
   env LD_LIBRARY_PATH=repositories/turtle/libturtle/.libs #{exe}"
end

Langs = {
  "kaplan" => KaplanRunner,
  "turtle" => TurtleRunner,
  "prolog" => "prolog -t 'bench(100).'"
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
  all = %w[animals layout sendmoremoney].map do |benchmark|
    namespace benchmark do
      all = %w[rb js prolog kaplan turtle].map do |lang|
        desc "Run cross-language benchmark #{benchmark} on #{lang}"
        task lang do
          cmdline = Langs[lang].go("benchmark-constraint-languages/#{benchmark}.#{lang}")
          puts cmdline
          system cmdline
        end
        lang
      end
      desc "Run all comparisons for #{benchmark}"
      task :all => all do
      end
    end
    benchmark
  end
  desc "Run all comparison benchmarks"
  task :all => all do
  end
end
