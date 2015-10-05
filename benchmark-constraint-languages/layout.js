function fun() {
    var solver = new ClSimplexSolver();
    var obj = {gap: 0,
               pw: 0,
               lw: 0,
               rw: 0};
    bbb.always({solver: solver,  ctx: {obj: obj}}, function () { return obj.pw == 40000 });
    bbb.always({solver: solver,  ctx: {obj: obj}}, function () { return obj.gap == obj.pw / 20000 });
    bbb.always({solver: solver,  ctx: {obj: obj}}, function () { return obj.lw + obj.gap + obj.rw == obj.pw });
    bbb.always({solver: solver,  ctx: {obj: obj}}, function () { return obj.lw >= 0 });
    bbb.always({solver: solver,  ctx: {obj: obj}}, function () { return obj.rw >= 0 });
    console.log("gap " + obj.gap + ", left column " + obj.lw + ", right column " + obj.rw + ", page width " + obj.pw)
}

var start = Date.now();
for(var i = 0; i < 10; i++) {
    fun()
}
console.log("THIS IS THE TIME:" + (Date.now() - start));
alert.original.apply(window, ["CLOSE ME"])
