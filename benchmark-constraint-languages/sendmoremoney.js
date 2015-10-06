CENTS = 10000
ANIMALS = 100
DOGC = 1500
CATC = 100
MICEC = 25
TIME_ = 0
REPEATS = 10

function action() {
    var solver = new EmZ3();
    var oldPM = solver.postMessage;
    solver.postMessage = function(string) {
        return oldPM.apply(solver, [string.replace(/Real/g, "Int")]);
    }

    setTimeout(function () {
        var start = Date.now();
        var obj = {s: 0, e: 0, n: 0, d: 0, m: 0, o: 0, r: 0, y:0};
        var names = ["s", "e", "n", "d", "m", "o", "r", "y"];
        var fo;
        names.forEach(function (f) {
            bbb.always({
                solver: solver,
                ctx: {obj: obj, f: f}}, function () {
                    return obj[f] <= 9 && obj[f] >= 0 });
        });
        bbb.always({
            solver: solver,
            ctx: {obj: obj}}, function () {
                return obj.s != 0 && obj.m != 0 });
        names.forEach(function (f) {
            names.forEach(function (fo) {
                if (f !== fo) {
                    bbb.always({
                        solver: solver,
                        ctx: {obj: obj, f: f, fo: fo}}, function () {
                            return obj[f] != obj[fo] });
                }
            })
        })

        bbb.always({
            solver: solver,
            ctx: {obj: obj}}, function () {
                return obj.s * 1000 + obj.e * 100 + obj.n * 10 + obj.d +
                    obj.m * 1000 + obj.o * 100 + obj.r * 10 + obj.e ==
                    obj.m * 10000 + obj.o * 1000 + obj.n * 100 + obj.e * 10 + obj.y });

        console.log("solution: [s,e,n,d,m,o,r,y] = " + [obj.s,obj.e,obj.n,obj.d,obj.m,obj.o,obj.r,obj.y])
        TIME_ += (Date.now() - start);

        if (REPEATS > 0) {
            REPEATS -= 1;
            setTimeout(action, 0);
        } else {
            console.log("THIS IS THE TIME:" + TIME_);
            alert.original.apply(window, ["CLOSE ME"])
        }
    }, 3000);
}

action()
