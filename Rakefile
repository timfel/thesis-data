ldpath = File.expand_path("../repositories/babelsberg-r/dependencies/z3/build", __FILE__)
Impls = {
  "rb" => "LD_LIBRARY_PATH=#{ldpath} repositories/babelsberg-r/bin/topaz",
  "st" => "squeak x86_64 runners/BabelsbergS.image ../",
  "js" => "nodejs runners/babelsberg-js-benchmarks.js"
}
Other = {
  "kaplan" => "repositories/scala-kaplan",
  "turtle" => "repositories/turtle"
}

%w[read-access write-access edit].each do |n|
  namespace n do
    Impls.each_pair do |name, cmd|
      desc "Run #{n} on #{name}"
      task name do
        cmdline = "#{cmd} benchmark-#{n}/benchmark.#{name}"
        puts cmdline
        system cmdline
      end
    end
  end
end

desc "Run JIT benchmarks"
task :jit do
  system "#{Impls['js']} benchmark-jit/benchmark.js"
end

desc "Run cross-language benchmarks"
task :compare do
  system "#{Impls['js']} benchmark-jit/benchmark.js"
end
