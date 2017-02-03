function ShirtViewModel(parent, initial){
    var my = {}; // Private variables
    var that = {}; // Public variables
    initial = initial || {};

    that.size = ko.observable(initial.size || "XS");
    that.style = ko.observable(initial.style || "Men's");
    that.colour = ko.observable(initial.colour || "Black print on white shirt");

    that.removeShirt = function () {
        parent.shirts.remove(function (s) {
            return s === that;
        });
    };

    that.asJSON = ko.pureComputed(function () {
        return {
            'size': that.size(),
            'style': that.style(),
            'colour': that.colour(),
        }
    });

    return that;
}

function OrderViewModel(initial) {
    var my = {}; // Private variables
    var that = {}; // Public variables
    initial = initial || {};

    that.firstName = ko.observable(initial.first_name || null);
    that.lastName = ko.observable(initial.last_name || null);
    that.email = ko.observable(initial.email || null);
    that.shirts = ko.observableArray(_.map(initial.shirts || [undefined], function (data) {
        return ShirtViewModel(that, data);
    })).extend({rateLimit: 10});

    that.shirts.subscribe(function (newval) {
        if (newval.length == 0){
            that.shirts.push(ShirtViewModel(that));
        }
    });

    that.paymentToken = ko.observable();

    that.asJSON = ko.pureComputed(function () {
        var shirts = that.shirts();
        var shirts_js_obj = [];
        for (var i = 0; i < shirts.length; i++){
            shirts_js_obj.push(shirts[i].asJSON());
        }
        return JSON.stringify({
            'first_name': that.firstName(),
            'last_name': that.lastName(),
            'email': that.email(),
            'shirts': shirts_js_obj,
            'payment_token': that.paymentToken(),
        });
    });

    that.newShirt = function () {
        that.shirts.push(ShirtViewModel(that));
    };

    that.submitText = ko.pureComputed(function () {
        var base = 'Pay Online ';
        var cost = that.shirts().length * 15;
        cost *= 1.0175;
        cost += 0.3;
        cost *= 100;
        cost |= 0;
        cost /= 100;
        return base + '($' + cost + ')';
    });

    that.asJSON.subscribe(console.log);
    return that;
}


VM = OrderViewModel(INITIAL_JSON);
ko.applyBindings(VM);