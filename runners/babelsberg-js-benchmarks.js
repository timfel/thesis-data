var browser = require("zombie").create();
var benchmarkfile = "../" + process.argv[2];

browser.visit("file://" + process.cwd() + "/runners/babelsbergjs.bench.html?file=" + benchmarkfile, function () {
    // if (browser.errors.length > 0) {
    //     throw ["Errors:"].concat(browser.errors).join("\n");
    // }
    // console.log("Tests run: " + browser.window.runcount);
    // if (browser.window.GlobalErrors.length != 0) {
    //     throw ["Errors: " + browser.window.GlobalErrors.length].concat(
    //         browser.window.GlobalErrors
    //     ).join("\n");
    // }
});
