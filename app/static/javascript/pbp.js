// Generated by CoffeeScript 1.9.3
(function() {
  var Accordian, LoadRiders, PbpRiderTable, d, drawRow, drawTable, i, m1, m2, next, root, spData, start;

  d = React.DOM;

  React.initializeTouchEvents(true);

  i = 0;

  start = void 0;

  m1 = void 0;

  m2 = void 0;

  next = void 0;

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  spData = null;

  root.doData = function(json) {
    spData = json.feeReact.DOM.entry;
  };

  ({
    drawCell: function(tr, val) {
      var tdd;
      tdd = $('<td/>');
      tr.append(td);
      tReact.DOM.append(val);
      return td;
    }
  });

  drawRow = function(table, rowData) {
    var c, tr;
    if (rowData === null) {
      return null;
    }
    if (rowData.length === 0) {
      return null;
    }
    tr = $('<tr/>');
    table.append(tr);
    c = 0;
    while (c < rowData.length) {
      drawCell(tr, rowData[c]);
      c++;
    }
    return tr;
  };

  drawTable = function(parent) {
    var table;
    table = $('<table/>');
    parent.append(table);
    return table;
  };

  root.readData = function(parent) {
    var cell, data, headers, pbpRiderInfo, r, rowData, val;
    data = spData;
    rowData = [];
    headers = [];
    pbpRiderInfo = [];
    r = 0;
    while (r < data.length) {
      cell = data[r]['gs$cell'];
      val = cell['$t'];
      if (cell.row == 1) {
        headers.push(val);
      } else if (cell.col == 1 && cell.row > 2) {
        pbpRiderInfo.push(rowData);
      }
      if (cell.col == 1) {
        rowData = [];
      }
      rowData.push(val);
      r++;
    }
    pbpRiderInfo.push(rowData);
    return _.map(pbpRiderInfo, function(rider) {
      return _.object(headers, rider);
    });
  };

  PbpRiderTable = React.createClass({
    getInitialState: function() {
      return {
        checkPoints: ["START", "MORTAGNE", "VILLAINES", "FOUGERES", "TINTENIAC", "LOUDEAC", "CARHAIX", "BREST", "CARHAIX", "LOUDEAC", "TINTENIAC", "FOUGERES", "VILLAINES", "MORTAGNE", "DREUX", "FINISH"],
        km: [0, 140, 221, 310, 364, 449, 525, 618, 703, 782, 867, 921, 1009, 1090, 1165, 1230],
        data: null
      };
    },
    componentDidMount: function() {
      return $.ajax({
        url: '/pbp_rider_status',
        data: {
          fram: this.props.fram
        },
        success: (function(_this) {
          return function(strData) {
            var temps;
            if (strData.message === "Success") {
              temps = strData.resp.split(';');
              if (_this.isMounted) {
                return _this.setState({
                  data: temps
                });
              }
            } else {
              return _this.setState({
                data: []
              });
            }
          };
        })(this),
        error: (function(_this) {
          return function() {
            if (_this.isMounted) {
              _this.setState({
                data: []
              });
            }
          };
        })(this),
        type: "GET",
        async: false,
        cache: true
      });
    },
    conv_min: function(temps) {
      var min, t;
      t = temps.split(':');
      min = parseInt(t[0] * 60) + parseInt(t[1]);
      return min;
    },
    conv_heure: function(temps) {
      var h, min;
      if (parseInt(temps) > 0) {
        h = parseInt(temps / 60);
        min = temps - (h * 60);
        if (min < 10) {
          min = '0' + min;
        }
        if (h < 10) {
          h = '0' + h;
        }
        return h + ':' + min;
      } else {
        return '';
      }
    },
    aff_heure: function(data) {
      var aff;
      aff = this.conv_heure(this.conv_min(this.state.data[i]) - start);
      return aff;
    },
    aff_date: function(data) {
      var dd, t;
      if (data[i] !== '') {
        dd = 16;
        t = this.conv_min(this.state.data[i]);
        while (t > 1440) {
          t = t - 1440;
          dd++;
        }
        return dd + '/08 ' + this.conv_heure(t);
      } else {
        return '';
      }
    },
    aff_date_min: function(min) {
      var dd, t;
      dd = 16;
      t = min;
      while (t > 1440) {
        t = t - 1440;
        d++;
      }
      return d + '/08 ' + this.conv_heure(t);
    },
    aff_km: function(data) {
      var aff_moy;
      if (data[i] !== '') {
        next = i;
        return this.state.km[i];
      } else {
        return '';
      }
    },
    aff_moy: function(data) {
      var r;
      if (data[i] !== '' && i > 0) {
        if (data[i - 1] !== '') {
          r = parseInt((this.state.km[i] - this.state.km[i - 1]) / (this.conv_min(this.state.data[i]) - this.conv_min(this.state.data[i - 1])) * 600) / 10 + ' km/h';
          m1 = r;
          return r;
        }
      }
      return '';
    },
    aff_moytot: function(data) {
      var r;
      if (data[i] !== '' && i > 0) {
        if (data[i - 1] !== '') {
          r = parseInt(this.state.km[i] / (this.conv_min(this.state.data[i]) - this.conv_min(this.state.data[0])) * 600) / 10 + ' km/h';
          i++;
          m2 = r;
          return r;
        }
      }
      i++;
      return '';
    },
    makeRow: function(location) {
      var rows;
      rows = [React.DOM.td({}, location), React.DOM.td({}, this.aff_km(this.state.data)), React.DOM.td({}, this.aff_heure(this.state.data))];
      if (location === 'FINISH') {
        if (this.state.data[17] === '' || this.state.data[17] === 'OK') {
          rows.push(React.DOM.td({}, this.aff_date(this.state.data)));
        } else if (this.state.data[17] === 'AB') {
          rows.push(React.DOM.td({}, "Abandon"));
        } else if (this.state.data[17] === 'NP') {
          rows.push(React.DOM.td({}, "Non Partant"));
        }
      } else {
        rows = rows.concat([React.DOM.td({}, this.aff_date(this.state.data), React.DOM.td({}, this.aff_moy(this.state.data), React.DOM.td({}, this.aff_moytot(this.state.data))))]);
      }
      return React.DOM.tr({}, rows);
    },
    render: function() {
      var extra, t, t1, t2, table, to_ret;
      to_ret = [];
      if (this.state.data === null) {
        return React.DOM.p({}, "loading...");
      } else if (this.state.data.length) {
        start = this.conv_min(this.state.data[0]);
        table = React.DOM.table({
          border: 1
        }, React.DOM.tr({}, React.DOM.td({
          width: '100'
        }, "Contrôle"), React.DOM.td({
          width: '100'
        }, "KM"), React.DOM.td({
          width: '100'
        }, "Temps"), React.DOM.td({
          width: '150'
        }, "Passage"), React.DOM.td({}, "Moyenne tronçon"), React.DOM.td({}, "Moyenne Totale")), this.state.checkPoints.map((function(_this) {
          return function(location) {
            return _this.makeRow(location);
          };
        })(this)));
        to_ret.push(table);
        if (next === 0) {
          m1 = '20 km/h';
          m2 = '35 km/h';
        }
        if (next < 15) {
          m1 = parseInt(m1.split(' ')[0]);
          m2 = parseInt(m2.split(' ')[0]);
          t1 = (this.state.km[next + 1] - this.state.km[next]) / m1 * 60 + this.conv_min(this.state.data[next]);
          t2 = (this.state.km[next + 1] - this.state.km[next]) / m2 * 60 + this.conv_min(this.state.data[next]);
          if (t1 > t2) {
            t = t1;
            t1 = t2;
            t2 = t;
          }
          extra = React.DOM.p({}, "Heure estimée d'arrivée au prochain contrôle entre " + (this.aff_date_min(t1)) + " et " + (this.aff_date_min(t2)));
          to_ret.push(extra);
        }
        i = 0;
        return table;
      } else {
        return React.DOM.p({}, "no results :(");
      }
    }
  });

  Accordian = React.createClass({
    getInitialState: function() {
      return {
        loadRequested: false,
        previousClick: null
      };
    },
    onClick: function() {
      $("[class~=collapse]").collapse("hide");
      $("#collapse-" + this.props.entry.fram).collapse('toggle');
      return this.setState({
        loadRequested: true
      });
    },
    makeHeader: function() {
      return React.DOM.h4({
        className: "panel-title"
      }, React.DOM.a({
        "data-toggle": "collapse",
        "data-parent": "#accordian",
        onClick: (function(_this) {
          return function() {
            return _this.onClick();
          };
        })(this),
        onTouchEnd: (function(_this) {
          return function() {
            return _this.onClick();
          };
        })(this)
      }, this.props.entry.first + " " + this.props.entry.last));
    },
    render: function() {
      return React.DOM.div({
        className: "panel panel-default",
        key: this.props.entry.fram
      }, React.DOM.div({
        className: "panel-heading"
      }, this.makeHeader()), React.DOM.div({
        id: "collapse-" + this.props.entry.fram,
        className: "panel-collapse collapse"
      }, React.DOM.div({
        className: "panel-body"
      }, React.DOM.div({
        className: "well"
      }, React.DOM.p({}, "Wave: " + this.props.entry.wave), React.DOM.p({}, "Start: " + this.props.entry.start + " hour"), React.DOM.p({}, "Group: " + this.props.entry['club_name'])), this.state.loadRequested ? PbpRiderTable({
        fram: this.props.entry.fram
      }) : React.DOM.div({}, ""))));
    }
  });

  LoadRiders = React.createClass({
    getInitialState: function() {
      return {
        dataUrl: "/pbp_riders",
        riders: [],
        loadingText: "Grabbing info",
        filterBy: "",
        name: "",
        email: "",
        rider_info: ""
      };
    },
    componentDidMount: function() {
      return $.get(this.state.dataUrl, (function(_this) {
        return function(data) {
          if (_this.isMounted) {
            return _this.setState({
              riders: data.data
            });
          }
        };
      })(this));
    },
    filterByName: function() {
      return _.filter(this.state.riders, (function(_this) {
        return function(entry) {
          return entry.full_name.toLowerCase().indexOf(_this.state.filterBy.toLowerCase()) > -1;
        };
      })(this));
    },
    getDropdowns: function() {
      var uniqClubs;
      uniqClubs = _.unique(_.map(riders, function(rider) {
        return rider.club_name;
      }));
      return React.DOM.select({
        className: "form-control"
      }, _.map(uniqClubs, function(club) {
        return React.DOM.option({
          value: club
        }, club);
      }));
    },
    handleEmailSubmit: function(event) {
      event.preventDefault();
      return $.ajax({
        url: '/pbp_rider_request',
        data: {
          name: this.state.name,
          email: this.state.email,
          rider_name: this.state.rider_name
        },
        success: function() {
          return console.log("winner");
        },
        error: function() {
          return console.log("it failed");
        },
        type: "POST"
      });
    },
    navBar: function() {
      return React.DOM.nav({
        className: "navbar navbar-default"
      }, React.DOM.div({
        className: "container-fluid"
      }, React.DOM.div({
        className: "navbar-header"
      }, React.DOM.p({
        className: "navbar-brand"
      }, "PBP")), React.DOM.div({
        className: "collapse navbar-collapse",
        id: "pbp-navbar"
      }, React.DOM.ul({
        className: "nav navbar-nav"
      }, React.DOM.li({}, React.DOM.a({
        href: "#"
      }, "Link")), this.getDropdowns()))));
    },
    render: function() {
      window.riders = this.state.riders;
      return React.DOM.div({
        className: "col-md-12"
      }, React.DOM.div({
        className: "row"
      }, React.DOM.div({}, React.DOM.div({
        className: "col-md-3 col-xs-12 col-s-12"
      }, React.DOM.div({
        className: "well"
      }, React.DOM.p({}, "Hi there! Please email me at rjames86@gmail.com if you have any feedback or want to add a rider."), React.DOM.p({}, "Thanks!"), React.DOM.p({}, "-Ryan")))), React.DOM.div({
        className: "col-md-6 col-xs-12 col-s-12"
      }, React.DOM.div({
        className: "panel-group",
        id: "accordian"
      }, this.state.filterBy.length ? this.filterByName().map(function(entry) {
        return Accordian({
          entry: entry
        });
      }) : this.state.riders.map(function(entry) {
        return Accordian({
          entry: entry
        });
      })))));
    }
  });

  $(function() {
    return React.render(LoadRiders({}), document.getElementById('react'));
  });

}).call(this);