require "libz3"

def fun
  gap, pw, lw, rw = [0]*4

  c1 = always { pw == 40000 }
  c2 = always { gap == pw / 20000 }
  c3 = always { lw + gap + rw == pw }
  c4 = always { lw >= 0 }
  c5 = always { rw >= 0 }

  puts "gap #{gap}, left column #{lw}, right column #{rw}, page width #{pw}"
  [c1,c2,c3,c4,c5].each(&:disable)
end

start = Time.now
10.times do
  fun
end
puts "THIS IS THE TIME: #{Time.now - start}"
