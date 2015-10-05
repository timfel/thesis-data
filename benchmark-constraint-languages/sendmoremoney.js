CENTS = 10000
ANIMALS = 100
DOGC = 1500
CATC = 100
MICEC = 25
TIME_ = 0
REPEATS = 50

console.log("Spend exactly #{CENTS / 100} dollars and buy exactly #{ANIMALS} animals. Dogs cost")
console.log("15 dollars, cats cost 1 dollar, and mice cost 25 cents each. You")
console.log("have to buy at least one of each. How many of each should you buy?")
function action() {
    var solver = new EmZ3();
    var oldPM = solver.postMessage;
    solver.postMessage = function(string) {
        return oldPM.apply(solver, [string.replace(/Real/g, "Int")]);
    }

    setTimeout(function () {
        var start = Date.now();
        var obj = {s: 0, e: 0, n: 0, d: 0, m: 0, o: 0, r: 0, y:0};
        var fo;
        for (var f in obj) {
            bbb.always({
                solver: solver,
                ctx: {obj: obj, f: f, fo: fo}}, function () {
                    return obj[f] <= 9 && obj[f] >= 0 });
            for (var fo in obj) {
                if (f !== fo) {
                    bbb.always({
                        solver: solver,
                        ctx: {obj: obj, f: f, fo: fo}}, function () {
                            return obj[f] != obj[fo] });
                }
            }
        }


        bbb.always({
            solver: solver,
            ctx: {obj: obj}}, function () {
                obj.s * 1000 + obj.e * 100 + obj.n * 10 + obj.d +
                    obj.m * 1000 + obj.o * 100 + obj.r * 10 + obj.e ==
                    obj.m * 10000 + obj.o * 1000 + obj.n * 100 + obj.e * 10 + obj.y });

        bbb.always({
            solver: solver,
            ctx: {obj: obj}}, function () {
                obj.s > 0 && obj.m > 0 });

        console.log("solution: [s,e,n,d,m,o,r,y] = " + [obj.s,obj.e,obj.n,obj.d,obj.m,obj.o,obj.r,obj.y])
        TIME_ += (Date.now() - start);

        if (REPEATS > 0) {
            REPEATS -= 1;
            setTimeout(action, 10);
        } else {
            console.log(TIME_);
        }
    }, 10000);
}

action()
