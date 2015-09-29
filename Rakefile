DevDir = File.expand_path("~/Dev/")
BabelsbergR = File.join(DevDir, "babelsberg-r")
BabelsbergS = File.join(DevDir, "babelsberg-s")
BabelsbergJS = File.join(DevDir, "babelsberg-js")
BabelsbergRML = File.join(DevDir, "babelsberg-rml")
Impls = [BabelsbergR, BabelsbergS, BabelsbergJS, BabelsbergRML]

task :rsync do
  Impls.each do |path|
    system "rsync -a --delete --progress \"#{path}\" repositories/"
  end
end

group :benchmarks do
  Impls[0...-1].each do |impl|
    i = impl.split("/").last
  end
  task :benchmarks => :dependencies do
    system "node babelsberg-js-benchmarks.js"
    ldpath = File.expand_path("../repositories/babelsberg-r/dependencies/z3/build", __FILE__)
    puts "LD_LIBRARY_PATH=#{ldpath} repositories/babelsberg-r/bin/topaz babelsberg-r-benchmarks.rb"
end

end

task :dependencies do
  system "npm install"
end
