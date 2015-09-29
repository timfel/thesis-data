// layout.t -- A simple layout example.
//
// Copyright (C) 2003 Martin Grabmueller <mgrabmue@cs.tu-berlin.de>
// 
// This is free software; you can redistribute it and/or modify it
// under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2, or (at your option)
// any later version.

module animals;

import io, sys.times;

fun test0()
  var cents: !int := var 0;
  var animals: !int := var 0;
  var dogc: !int := var 0;
  var catc: !int := var 0;
  var micec: !int := var 0;

  require cents = 10000;
  require animals = 100;
  require dogc = 1500;
  require catc = 100;
  require micec = 25;

  var dog: !int := var 0;
  var cat: !int := var 0;
  var mouse: !int := var 0;

  require dog >= 1;
  require cat >= 1;
  require mouse >= 1;
  require dog < animals;
  require cat < animals;
  require mouse < animals;
  require dog + cat + mouse = animals;
  require dog * dogc + cat * catc + mouse * micec = cents;

  io.put ("Dogs: "); io.put (!dog);
  io.put (", cats: "); io.put (!cat);
  io.put (", mice: "); io.put (!mouse); io.nl ();
end;

fun main(args: list of string): int
  var start: long := sys.times.time();
  test0();
  io.put (sys.times.time() - start);
  io.nl ();
  return 0;
end;


// End of layout.t.
