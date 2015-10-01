suite = new Benchmark.Suite;

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
    "Declarative Drag": [resetConstraints = function() {
        ctx = {
            mouse: {location_y: 0},
            mercury: {top: 0, bottom: 0},
            thermometer: {top: 0, bottom: 0},
            temperature: {c: 0},
            gray: {top: 0, bottom: 0},
            white: {top: 0, bottom: 0},
            display: {number: 0}};
        solver = new ClSimplexSolver();
        bbb.always({solver: solver, ctx: ctx}, function () { return temperature.c == mercury.top });
        bbb.always({solver: solver, ctx: ctx}, function () { return white.top == thermometer.top });
        bbb.always({solver: solver, ctx: ctx}, function () { return white.bottom == mercury.top });
        bbb.always({solver: solver, ctx: ctx}, function () { return gray.top == mercury.top });
        bbb.always({solver: solver, ctx: ctx}, function () { return gray.bottom == mercury.bottom });
        bbb.always({solver: solver, ctx: ctx}, function () { return display.number == temperature.c });
        bbb.always({solver: solver, ctx: ctx}, function () { return mercury.top == mouse.location_y });
        bbb.always({solver: solver, ctx: ctx}, function () { return mercury.top <= thermometer.top });
        bbb.always({solver: solver, ctx: ctx}, function () { return mercury.bottom == thermometer.bottom });
    }, function() {
        for (var i = 0; i < 100; i++) {
            ctx.mouse.location_y = i
        }
    }],
    "Edit Drag": [function() {
        resetConstraints();
        cb = bbb.edit(ctx.mouse, ["location_y"]);
    }, function() {
        for (var i = 0; i < 100; i++) {
            cb([i]);
        }
    }]
}

for (var k in benchmarks) {
    suite.add(k, benchmarks[k][1], {setup: benchmarks[k][0]})
}

suite.on('cycle', function(event) {
    console.log(String(event.target));
}).on('complete', function() {
    console.log('Fastest is ' + this.filter('fastest').pluck('name'));
}).run({ 'async': false });
