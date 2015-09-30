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

suite.add('Unconstrained Write', function() {
    sumObj.a += sumObj.b += sumObj.c += sumObj.d += sumObj.e += 1
}).add('Properties Write', function() {
    sumObj2.a += sumObj2.b += sumObj2.c += sumObj2.d += sumObj2.e += 1
}).add('Constrained Write', function() {
    constrainedSumObj.a += constrainedSumObj.b +
        constrainedSumObj.c += constrainedSumObj.d += constrainedSumObj.e += 1
}).add('Constrained Write (disabled)', function() {
    constraint.disable();
    constrainedSumObj.a += constrainedSumObj.b +
        constrainedSumObj.c += constrainedSumObj.d += constrainedSumObj.e += 1
}).add('Constrained Write (disabled, unconstrained)', function() {
    constraint.disable();
    bbb.unconstrain(constrainedSumObj);
    constrainedSumObj.a += constrainedSumObj.b +
        constrainedSumObj.c += constrainedSumObj.d += constrainedSumObj.e += 1
}).on('cycle', function(event) {
    console.log(String(event.target));
}).on('complete', function() {
    console.log('Fastest is ' + this.filter('fastest').pluck('name'));
}).run({ 'async': false });
