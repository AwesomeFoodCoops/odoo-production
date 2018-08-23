odoo.define('coop_memberspace.statistics', function (require) {
    "use strict";

    var snippet_animation = require('web_editor.snippets.animation');
    var session = require('web.session');
    var Model = require('web.Model');
    var ajax = require("web.ajax");

    snippet_animation.registry.statistics =
		snippet_animation.Class.extend({
            selector: '.chart-statistics',
            start: function () {
                var self = this;
                ajax.jsonRpc("/web/session/get_session_info", "call").then(function (sessiondata) {
                    self.session = sessiondata;
                });
                new Model('res.users').call('get_statistics_char', [])
                .then(function(datas) {
                    var backgroundColor = [];
                    var value = [];
                    datas.forEach(function(item){
                        backgroundColor.push(item.color);
                        value.push(item.value);
                    });
                    console.log(">>>>>>>>>>>>>>> value", value);
                    var data = {
                        labels: ["Janv.", "Fev.", "Mars", "Avril", "Mai", "Juin", "Juil", "Août", "Sept.", "Oct.", "Nov.", "Dec."],
                        datasets: [{
                            label: "Chiffre d’affaires mensuel (k€ TTC)",
                            // borderColor: "#7f7575",
                            // borderWidth: 2,
                            hoverBackgroundColor: "#efeb1d",
                            // hoverBorderColor: "#7f7575",
                            backgroundColor: backgroundColor,
                            data: value,
                        }]
                    };

                    var options = {
                        tooltips: {
                            callbacks: {
                                label: function(tooltipItem, data) {
                                    return Math.round(tooltipItem.yLabel * 100) / 100;
                                }
                            }
                        },
                        legend: {
                            display: false
                        },
                        maintainAspectRatio: false,
                        scales: {
                            yAxes: [{
                            stacked: true,
                            gridLines: {
                                display: true,
                                color: "rgba(255,99,132,0.2)"
                            }
                            }],
                            xAxes: [{
                            gridLines: {
                                display: false
                            }
                            }]
                        },
                    };

                    Chart.Bar('chart', {
                        options: options,
                        data: data
                    });
                });
            }
        })
});
