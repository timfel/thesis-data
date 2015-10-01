var suite = new Benchmark.Suite;

benchf = function() {
    obj.a + obj.b + obj.c + obj.d + obj.e
}
benchmarks = {
    "Unconstrained Read": [initf = function() {
        obj = {a: 1, b: 1, c:1, d:1, e:1};
    }, benchf],
    "Properties Read": [function() {
        obj = {
            get a() { return this.$$a }, $$a: 0,
            get b() { return this.$$b }, $$b: 0,
            get c() { return this.$$c }, $$c: 0,
            get d() { return this.$$d }, $$d: 0,
            get e() { return this.$$e }, $$e: 0,
        }
    }, benchf],
    "Constrained Read": [constrainf = function() {
        initf()
        constraint = bbb.always({solver: new ClSimplexSolver(), ctx: {obj: obj}}, function () {
            return obj.a == 1 &&
                obj.b == 1 &&
                obj.c == 1 &&
                obj.d == 1 &&
                obj.e == 1
        });
    }, benchf],
    "Constrained Read (disabled)": [disablef = function() {
        constrainf()
        constraint.disable();
    }, benchf],
    "Constrained Read (disabled, unconstrained)": [function() {
        disablef();
        bbb.unconstrainAll(obj);
    }, benchf]
}

for (var k in benchmarks) {
    suite.add(k, benchmarks[k][1], {setup: benchmarks[k][0]})
}

suite.on('cycle', function(event) {
    console.log(String(event.target));
}).on('complete', function() {
    console.log('Fastest is ' + this.filter('fastest').pluck('name'));
}).run({ 'async': false });
