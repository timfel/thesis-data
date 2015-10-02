var suite = new Benchmark.Suite;

benchmarks = {
    "Imperative Drag": [function() {
        mouse = {location_y: 0},
        mercury = {top: 0, bottom: 0},
        thermometer = {top: 0, bottom: 0},
        temperature = 0,
        gray = {top: 0, bottom: 0},
        white = {top: 0, bottom: 0},
        display = {number: 0};
    }, function() {
        for (var i = 0; i < 100; i++) {
            mouse.location_y = i
            var old = mercury.top
            mercury.top = mouse.location_y
            if (mercury.top > thermometer.top) {
                mercury.top = thermometer.top
            }
            temperature = mercury.top
            if (old < mercury.top) {
                // moves upwards (draws over the white)
                gray.top = mercury.top
            } else {
                // moves downwards (draws over the gray)
                white.bottom = mercury.top
            }
            display.number = temperature
        }
    }],
    "Declarative Drag (Classic JIT)": [constrainf = function(jit) {
        ctx = {
            mouse: {location_y: 0},
            mercury: {top: 0, bottom: 0},
            thermometer: {top: 0, bottom: 0},
            temperature: {c: 0},
            gray: {top: 0, bottom: 0},
            white: {top: 0, bottom: 0},
            display: {number: 0}};
        solver = new ClSimplexSolver();
        solver.ecjit = jit || new ClassicECJIT();
        bbb.always({solver: solver, ctx: ctx}, function () { return temperature.c == mercury.top });
        bbb.always({solver: solver, ctx: ctx}, function () { return white.top == thermometer.top });
        bbb.always({solver: solver, ctx: ctx}, function () { return white.bottom == mercury.top });
        bbb.always({solver: solver, ctx: ctx}, function () { return gray.top == mercury.top });
        bbb.always({solver: solver, ctx: ctx}, function () { return gray.bottom == mercury.bottom });
        bbb.always({solver: solver, ctx: ctx}, function () { return display.number == temperature.c });
        bbb.always({solver: solver, ctx: ctx}, function () { return mercury.top == mouse.location_y });
        bbb.always({solver: solver, ctx: ctx}, function () { return mercury.top <= thermometer.top });
        bbb.always({solver: solver, ctx: ctx}, function () { return mercury.bottom == thermometer.bottom });
    }, benchf = function() {
        for (var i = 0; i < 100; i++) {
            ctx.mouse.location_y = i
        }
    }],
    "Declarative Drag (Additive JIT)": [
        function() { constrainf(new AdditiveAdaptiveECJIT()) },
        benchf
    ],
    "Declarative Drag (Multiplicative JIT)": [
        function() { constrainf(new MultiplicativeAdaptiveECJIT()) },
        benchf
    ],
    "Declarative Drag (Last JIT)": [
        function() { constrainf(new LastECJIT()) },
        benchf
    ],
}

for (var k in benchmarks) {
    // suite.add(k, benchmarks[k][1], {setup: benchmarks[k][0]})
}

ecbenchmarks1 = {
    'dbAddSim': [
        function(ecjit) {
            o = {x: 0, y: 0, z: 0};
            solver = new DBPlanner();
            solver.ecjit = ecjit;

            bbb.always({solver: solver, ctx: {o: o}}, function () {
                return o.x == o.z - o.y &&
                    o.y == o.z - o.x &&
                    o.z == o.x + o.y;
            })
        }, function(iterations) {
            for (var i = 0; i < iterations; i++) {
                o.x = i;
                console.assert(o.x + o.y == o.z);
            }
        }, function(iterations) {
            cb = bbb.edit(o, ["x"]);
            for (var i = 0; i < iterations; i++) {
                cb([i]);
                console.assert(o.x + o.y == o.z);
            }
            cb();
        }],
    'clAddSim': [
        function(ecjit) {
            o = {x: 0, y: 0, z: 0};
            solver = new ClSimplexSolver();
            solver.ecjit = ecjit;
            solver.setAutosolve(false);
            bbb.always({solver: solver, ctx: {o: o}}, function () { return o.x + o.y == o.z; });
        }, function(iterations) {
            for (var i = 0; i < iterations; i++) {
                o.x = i;
                console.assert(o.x + o.y == o.z);
            }
        }, function() {
            cb = bbb.edit(o, ["x"]);
        }, function (iterations) {
            for (var i = 0; i < iterations; i++) {
                cb([i]);
                console.assert(o.x + o.y == o.z);
            }
        }],
    'clDragSim': [
        function(ecjit) {
            ctx = {
                mouse: {location_y: 0},
                mercury: {top: 0, bottom: 0},
                thermometer: {top: 0, bottom: 0},
                temperature: {c: 0},
                gray: {top: 0, bottom: 0},
                white: {top: 0, bottom: 0},
                display: {number: 0}},
            solver = new ClSimplexSolver();
            solver.ecjit = ecjit;
            solver.setAutosolve(false);

            bbb.always({solver: solver, ctx: ctx}, function () { return temperature.c == mercury.top });
            bbb.always({solver: solver, ctx: ctx}, function () { return white.top == thermometer.top });
            bbb.always({solver: solver, ctx: ctx}, function () { return white.bottom == mercury.top });
            bbb.always({solver: solver, ctx: ctx}, function () { return gray.top == mercury.top });
            bbb.always({solver: solver, ctx: ctx}, function () { return gray.bottom == mercury.bottom });
            bbb.always({solver: solver, ctx: ctx}, function () { return display.number == temperature.c });
            bbb.always({solver: solver, ctx: ctx}, function () { return mercury.top == mouse.location_y });
            bbb.always({solver: solver, ctx: ctx}, function () { return mercury.top <= thermometer.top });
            bbb.always({solver: solver, ctx: ctx}, function () { return mercury.bottom == thermometer.bottom });
        }, function(iterations) {
            for (var i = 0; i < iterations; i++) {
                ctx.mouse.location_y = i;
                console.assert(ctx.mouse.location_y == i);
            }
        }, function() {
            cb = bbb.edit(ctx.mouse, ["location_y"]);
        }, function(iterations) {
            for (var i = 0; i < iterations; i++) {
                cb([i]);
                console.assert(ctx.mouse.location_y == i);
            }
        }],
}

jits = ['EmptyECJIT', 'ClassicECJIT', 'AdditiveAdaptiveECJIT', 'MultiplicativeAdaptiveECJIT', 'LastECJIT']
iterations = 1;

var idx = 0
function wrap(options, fn) {
    var str = fn.toString();
    for (var k in options) {
        window[k + idx] = options[k];
        str = str.replace(RegExp("([^a-zA-Z])" + k + "([^a-zA-Z0-9])", "g"), "$1" + k + idx + "$2");
        idx += 1;
    }
    return eval("(" + str + ")");
}

for (var k in ecbenchmarks1) {
    jits.each(function (jit) {
        ecjit = eval(jit)
        suite.add(k + " " + jit, wrap({k: k, iterations: iterations}, function() {
            ecbenchmarks1[k][1](iterations)
        }), {setup: wrap({k: k, ecjit: ecjit}, function() {
            ecbenchmarks1[k][0](new ecjit)
        })})
    });
    suite.add(k + " Edit Constraints", wrap({k: k, iterations: iterations}, function() {
        ecbenchmarks1[k][3](iterations)
    }), {setup: wrap({k: k, ecjit: ecjit}, function() {
        ecbenchmarks1[k][2]()
    })})
}

[1, 3].each(function(sheer) {
    jits.each(function(jit) {
        var ecjit = new (eval(jit))
        var numIterations = iterations;
        var setup = function() {
            ctx = {
                mouse: {x: 100, y: 100},
                wnd: {w: 100, h: 100},
                comp1: {w: 70, display: 0},
                comp2: {w: 30, display: 0}
            };
            var solver = new ClSimplexSolver();
            solver.ecjit = ecjit;
            solver.setAutosolve(false);

            bbb.always({solver: solver, ctx: ctx}, function () { return wnd.w == mouse.x });
            bbb.always({solver: solver, ctx: ctx}, function () { return wnd.h == mouse.y });
            bbb.always({solver: solver, ctx: ctx}, function () { return comp1.w <= 400; });
            bbb.always({solver: solver, ctx: ctx}, function () { return comp1.w+comp2.w == wnd.w; });
            bbb.always({solver: solver, ctx: ctx}, function () { return comp1.display == wnd.w; });
            bbb.always({solver: solver, ctx: ctx}, function () { return comp2.display == wnd.h; });
        };
        suite.add('clDrag2DSim' + sheer + " " + jit,
                  wrap({sheer: sheer, numIterations: numIterations, ecjit: ecjit}, function() {
                      for(var i = 0; i < numIterations; i++) {
                          ctx.mouse.x = 100+i;
                          if(i % sheer == 0) {
                              ctx.mouse.y = 100+i;
                          }
                          console.assert(ctx.mouse.x == 100+i);
                          if(i % sheer == 0) {
                              console.assert(ctx.mouse.y == 100+i);
                          }
                      }
                  }),
                  {setup: wrap({sheer: sheer, numIterations: numIterations, ecjit: ecjit}, setup)});
        suite.add('clDrag2DSimEdit' + sheer + " " + jit,
                  wrap({sheer: sheer, numIterations: numIterations, ecjit: ecjit}, function(numIterations, sheer) {
                      for(var i = 0; i < numIterations; i++) {
                          cb([100+i, Math.floor((100+i)/sheer)*sheer]);
                          console.assert(ctx.mouse.x == 100+i);
                          console.assert(ctx.mouse.y == Math.floor((100+i)/sheer)*sheer);
                      }
                  }),
                  {setup: wrap({sheer: sheer, numIterations: numIterations, ecjit: ecjit}, function() {
                      setup();
                      cb = bbb.edit(ctx.mouse, ["x", "y"]);
                  })});
    });
});

[iterations / 2, iterations / 10].each(function(numSwitch) {
    jits.each(function(jit) {
        var ecjit = new (eval(jit))
        var numIterations = iterations;
        var setup = wrap({numSwitch: numSwitch, numIterations: numIterations, ecjit: ecjit}, function() {
            ctx = {
                mouse: {x: 100, y: 100},
                wnd: {w: 100, h: 100},
                comp1: {w: 70, display: 0},
                comp2: {w: 30, display: 0}
            };
            var solver = new ClSimplexSolver();
            solver.ecjit = ecjit;
            solver.setAutosolve(false);

            bbb.always({solver: solver, ctx: ctx}, function () { return wnd.w == mouse.x });
            bbb.always({solver: solver, ctx: ctx}, function () { return wnd.h == mouse.y });
            bbb.always({solver: solver, ctx: ctx}, function () { return comp1.w <= 400; });
            bbb.always({solver: solver, ctx: ctx}, function () { return comp1.w+comp2.w == wnd.w; });
            bbb.always({solver: solver, ctx: ctx}, function () { return comp1.display == wnd.w; });
            bbb.always({solver: solver, ctx: ctx}, function () { return comp2.display == wnd.h; });
        });
        suite.add('clDrag2DSimChange' + numSwitch + " " + jit,
                  wrap({numSwitch: numSwitch, numIterations: numIterations, ecjit: ecjit}, function() {
                      for(var i = 0; i < numIterations; i++) {
                          if(i < numSwitch) {
                              ctx.mouse.x = 100+i;
                              console.assert(ctx.mouse.x == 100+i);
                          } else {
                              ctx.mouse.y = 100+(i-numSwitch);
                              console.assert(ctx.mouse.x == numSwitch-1);
                              console.assert(ctx.mouse.y == 100+(i-numSwitch));
                          }
                      }
                  }),
                  {setup: setup});
        suite.add('clDrag2DSimChangeEdit' + numSwitch + " " + jit,
                  wrap({numSwitch: numSwitch, numIterations: numIterations, ecjit: ecjit}, function() {
                      for(var i = 0; i < numIterations; i++) {
                          if(i < numSwitch) {
                              cb([100+i]);
                              console.assert(ctx.mouse.x == 100+i);
                          } else {
                              if(i == numSwitch) {
                                  cb();
                                  cb = bbb.edit(ctx.mouse, ["y"]);
                              }
                              cb([100+(i-numSwitch)]);
                              console.assert(ctx.mouse.x == numSwitch-1);
                              console.assert(ctx.mouse.y == 100+(i-numSwitch));
                          }
                      }
                  }),
                  {setup: function() {
                      setup();
                      cb = bbb.edit(ctx.mouse, ["x"]);
                  }});
    });
});

[5, 10].each(function(switchFreq) {
    jits.each(function(jit) {
        var ecjit = new (eval(jit))
        var numIterations = iterations;
        var setup = wrap({switchFreq: switchFreq, numIterations: numIterations, ecjit: ecjit}, function() {
            ctx = {
                mouse: {x: 100, y: 100},
                wnd: {w: 100, h: 100},
                comp1: {w: 70, display: 0},
                comp2: {w: 30, display: 0}
            };
            var solver = new ClSimplexSolver();
            solver.ecjit = ecjit;
            solver.setAutosolve(false);

            bbb.always({solver: solver, ctx: ctx}, function () { return wnd.w == mouse.x });
            bbb.always({solver: solver, ctx: ctx}, function () { return wnd.h == mouse.y });
            bbb.always({solver: solver, ctx: ctx}, function () { return comp1.w <= 400; });
            bbb.always({solver: solver, ctx: ctx}, function () { return comp1.w+comp2.w == wnd.w; });
            bbb.always({solver: solver, ctx: ctx}, function () { return comp1.display == wnd.w; });
            bbb.always({solver: solver, ctx: ctx}, function () { return comp2.display == wnd.h; });
        });
        suite.add('clDrag2DSimFreqChange' + switchFreq + " " + jit,
                  wrap({switchFreq: switchFreq, numIterations: numIterations, ecjit: ecjit}, function() {
                      for(var i = 0; i < numIterations; i++) {
                          if(i % (switchFreq*2) < switchFreq) {
                              ctx.mouse.x = 100+i;
                              console.assert(ctx.mouse.x == 100+i);
                          } else {
                              ctx.mouse.y = 100+i;
                              console.assert(ctx.mouse.y == 100+i);
                          }
                      }

                  }),
                  {setup: setup});
        suite.add('clDrag2DSimChangeEdit' + switchFreq + " " + jit,
                  wrap({switchFreq: switchFreq, numIterations: numIterations, ecjit: ecjit}, function() {
                      for(var i = 0; i < numIterations; i++) {
                          if(i % (switchFreq*2) < switchFreq) {
                              cb([100+i, 100+i/(switchFreq*2)]);
                              console.assert(ctx.mouse.x == 100+i);
                          } else {
                              cb([100+i/(switchFreq*2), 100+i]);
                              console.assert(ctx.mouse.y == 100+i);
                          }
                      }
                  }),
                  {setup: function() {
                      setup();
                      cb = bbb.edit(ctx.mouse, ["x", "y"]);
                  }});
    });
});

suite.on('cycle', function(event) {
    console.log(String(event.target));
}).on('complete', function() {
    console.log('Fastest is ' + this.filter('fastest').pluck('name'));
}).run({ 'async': false });
