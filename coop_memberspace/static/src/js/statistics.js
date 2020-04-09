odoo.define('coop_memberspace.statistics', function(require) {
    "use strict";

    var sAnimations = require('website.content.snippets.animation');
    var session = require('web.session');
    var ajax = require("web.ajax");

    sAnimations.registry.statistics =
        sAnimations.Class.extend({
            selector: '.chart-statistics',
            start: function() {
                var self = this;
                ajax.jsonRpc("/web/session/get_session_info", "call").then(function(sessiondata) {
                    self.session = sessiondata;
                });
                self._rpc({
                        model: 'res.users',
                        method: 'get_statistics_char',
                        args: [],
                    })
                    .then(function(datas) {
                        var backgroundColor = [];
                        var value = [];
                        datas.forEach(function(item) {
                            backgroundColor.push(item.color);
                            value.push(item.value);
                        });
                        var data = {
                            labels: ["Janv.", "Fev.", "Mars", "Avril", "Mai", "Juin", "Juil.", "Août", "Sept.", "Oct.", "Nov.", "Dec."],
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