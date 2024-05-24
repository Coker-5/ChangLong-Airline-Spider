// e为航班代码，t为floatprice。此处为js破解
function dp(e, t) {
                if (e) {
                    var n = e.split("&");
                    return n.map(function(e, i) {
                        n[i] = (parseInt(e) - 7 - t) / (2 + i)
                    }),
                    String.fromCharCode.apply(this, n)
                }
            }
            console.log(dp("198",21))
