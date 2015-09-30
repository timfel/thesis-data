var suite = new Benchmark.Suite;

var Iterations = 1000
var sumObj = {a: 1, b: 1, c:1, d:1, e:1},
    sumObj2 = {
        get a() { return this.$$a }, $$a: 0,
        get b() { return this.$$b }, $$b: 0,
        get c() { return this.$$c }, $$c: 0,
        get d() { return this.$$d }, $$d: 0,
        get e() { return this.$$e }, $$e: 0,
    },
    constrainedSumObj = {a: 1, b: 1, c:1, d:1, e:1},
    constraint = bbb.always({solver: new ClSimplexSolver(), ctx: {obj: constrainedSumObj}}, function () {
        return obj.a >= 1 &&
            obj.b >= 1 &&
            obj.c >= 1 &&
            obj.d >= 1 &&
            obj.e >= 1
    });

suite.add('Imperative Drag Simulation', function() {
    var mouse = {},
        mercury = {},
        thermometer = {},
        temperature = 0,
        gray = {},
        white = {},
        display = {};

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
}).add('Declarative Drag Simulation', function() {
    var ctx = {
        mouse: {location_y: 0},
        mercury: {top: 0, bottom: 0},
        thermometer: {top: 0, bottom: 0},
        temperature: {c: 0},
        gray: {top: 0, bottom: 0},
        white: {top: 0, bottom: 0},
        display: {number: 0}},
        solver = new ClSimplexSolver();
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

    for (var i = 0; i < 100; i++) {
        ctx.mouse.location_y = i
    }
}).add('Edit Drag Simulation', function() {
    var ctx = {
        mouse: {location_y: 0},
        mercury: {top: 0, bottom: 0},
        thermometer: {top: 0, bottom: 0},
        temperature: {c: 0},
        gray: {top: 0, bottom: 0},
        white: {top: 0, bottom: 0},
        display: {number: 0}};
    var solver = new ClSimplexSolver();

    bbb.always({solver: solver, ctx: ctx}, function () { return temperature.c == mercury.top });
    bbb.always({solver: solver, ctx: ctx}, function () { return white.top == thermometer.top });
    bbb.always({solver: solver, ctx: ctx}, function () { return white.bottom == mercury.top });
    bbb.always({solver: solver, ctx: ctx}, function () { return gray.top == mercury.top });
    bbb.always({solver: solver, ctx: ctx}, function () { return gray.bottom == mercury.bottom });
    bbb.always({solver: solver, ctx: ctx}, function () { return display.number == temperature.c });
    bbb.always({solver: solver, ctx: ctx}, function () { return mercury.top == mouse.location_y });
    bbb.always({solver: solver, ctx: ctx}, function () { return mercury.top <= thermometer.top });
    bbb.always({solver: solver, ctx: ctx}, function () { return mercury.bottom == thermometer.bottom });

    var cb = bbb.edit(ctx.mouse, ["location_y"]);
    for (var i = 0; i < this.Iterations; i++) {
        cb(i);
    }
}).on('cycle', function(event) {
    console.log(String(event.target));
}).on('complete', function() {
    console.log('Fastest is ' + this.filter('fastest').pluck('name'));
}).run({ 'async': false });
