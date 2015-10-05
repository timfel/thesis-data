CENTS = 10000
ANIMALS = 100
DOGC = 1500
CATC = 100
MICEC = 25
TIME_ = 0
REPEATS = 10

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
        var obj = {cents: 0, animals: 0, dogc: 0, catc: 0, micec: 0};
        bbb.always({
            solver: solver,
            ctx: {obj: obj}}, function () {
                return obj.cents == CENTS &&
                    obj.animals == ANIMALS &&
                    obj.dogc == DOGC &&
                    obj.catc == CATC &&
                    obj.micec == MICEC });

        var obj2 = {dog: 0, cat: 0, mouse: 0};
        bbb.always({
            solver: solver,
            ctx: {obj2: obj2}}, function () { return obj2.dog >= 1 && obj2.cat >= 1 && obj2.mouse >= 1 });
        bbb.always({
            solver: solver,
            ctx: {obj: obj, obj2: obj2}}, function () { return obj2.dog + obj2.cat + obj2.mouse == obj.animals });
        bbb.always({
            solver: solver,
            ctx: {obj: obj, obj2: obj2}}, function () { return obj2.dog * obj.dogc + obj2.cat * obj.catc + obj2.mouse * obj.micec == obj.cents });
        console.log("Dogs: " + obj2.dog + ", cats: " + obj2.cat + ", mice: " + obj2.mouse)
        TIME_ += (Date.now() - start);

        if (REPEATS > 0) {
            REPEATS -= 1;
            setTimeout(action, 10000);
        } else {
            console.log("THIS IS THE TIME:" + TIME_);
            alert.original.apply(window, ["CLOSE ME"])
        }
    }, 10000);
}

action()
