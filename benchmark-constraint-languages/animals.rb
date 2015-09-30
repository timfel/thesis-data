require "libz3"

CENTS = 10000
ANIMALS = 100
DOGC = 1500
CATC = 100
MICEC = 25

puts "Spend exactly #{CENTS / 100} dollars and buy exactly #{ANIMALS} animals. Dogs cost"
puts "15 dollars, cats cost 1 dollar, and mice cost 25 cents each. You"
puts "have to buy at least one of each. How many of each should you buy?"
def action
  cents, animals, dogc, catc, micec = [0.0] * 5

  always { cents == CENTS &&
          animals == ANIMALS &&
          dogc == DOGC &&
          catc == CATC &&
          micec == MICEC }

  dog, cat, mouse = 0, 0, 0
  c1 = always { dog >= 1 && cat >= 1 && mouse >= 1 }
  c2 = always { dog + cat + mouse == animals }
  c3 = always {dog * dogc + cat * catc + mouse * micec == cents }
  puts "Dogs: #{dog}, cats: #{cat}, mice: #{mouse}"
  [c1,c2,c3].each(&:disable)
end

start = Time.now
5.times do
  action
end
puts "#{Time.now - start}"
