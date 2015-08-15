// Generated by CoffeeScript 1.9.3
(function() {
  var Accordian, LoadRiders, PbpRiderTable, d, drawCell, drawRow, drawTable, root, spData;

  d = React.DOM;

  root = typeof exports !== "undefined" && exports !== null ? exports : this;

  spData = null;

  root.doData = function(json) {
    spData = json.feed.entry;
  };

  drawCell = function(tr, val) {
    var td;
    td = $('<td/>');
    tr.append(td);
    td.append(val);
    return td;
  };

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
    i: 0,
    start: void 0,
    getInitialState: function() {
      return {
        checkPoints: ["START", "MORTAGNE", "VILLAINES", "FOUGERES", "TINTENIAC", "LOUDEAC", "CARHAIX", "BREST", "CARHAIX", "LOUDEAC", "TINTENIAC", "FOUGERES", "VILLAINES", "MORTAGNE", "DREUX", "FINISH"],
        data: null
      };
    },
    componentDidMount: function() {
      return $.ajax({
        url: 'http://suivi.paris-brest-paris.org/data/' + this.props.fram + '.txt',
        success: (function(_this) {
          return function(strData) {
            var temps;
            temps = strdata.split(';');
            if (_this.isMounted) {
              return _this.setState({
                data: temps
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
        cache: true,
        crossDomain: true,
        dataType: 'jsonp'
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
    aff_heure: function() {
      var aff;
      aff = conv_heure(conv_min(this.state.data[this.i]) - this.start);
      return aff;
    },
    aff_date: function() {
      var t;
      if (this.state.data[this.i] !== '') {
        d = 16;
        t = conv_min(this.state.data[this.i]) + conv_min('16:00');
        while (t > 1440) {
          t = t - 1440;
          d++;
        }
        i++;
        return d + '/08 ' + conv_heure(t);
      } else {
        return '';
      }
    },
    makeRow: function(location) {
      return d.tr({}, d.td({}, location), d.td({}, this.aff_heure(this.state.data)), location === 'FINISH' ? this.state.data[17] === '' || this.state.data[17] === 'OK' ? d.td({}, this.aff_date(this.state.data)) : this.state.data[17] === 'AB' ? d.td({}, "Abandon") : this.state.data[17] === 'NP' ? d.td({}, "Non Partant") : void 0 : d.td({}, this.aff_date));
    },
    render: function() {
      var table;
      if (this.state.data === null) {
        return d.p({}, "loading...");
      } else if (this.state.data.length) {
        this.start = conv_min(this.state.data[0]);
        table = d.table({
          border: 1
        }, d.tr({}, d.td({
          width: '100'
        }, "Contrôle"), d.td({
          width: '100'
        }, "Temps"), d.td({
          width: '150'
        }, "Passage")), this.state.checkPoints.map(function(location) {
          return this.makeRow(location);
        }));
        this.i = 0;
        return table;
      } else {
        return d.p({}, "no results :(");
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
      return d.h4({
        className: "panel-title"
      }, d.a({
        "data-toggle": "collapse",
        "data-parent": "#accordian",
        onClick: (function(_this) {
          return function() {
            return _this.onClick();
          };
        })(this)
      }, this.props.entry.first + " " + this.props.entry.last));
    },
    render: function() {
      return d.div({
        className: "panel panel-default"
      }, d.div({
        className: "panel-heading"
      }, this.makeHeader()), d.div({
        id: "collapse-" + this.props.entry.fram,
        className: "panel-collapse collapse"
      }, d.div({
        className: "panel-body"
      }, d.div({
        className: "well"
      }, d.p({}, "Wave: " + this.props.entry.wave), d.p({}, "Start: " + this.props.entry.start + " hour"), d.p({}, "Group: " + this.props.entry['club_name'])), this.state.loadRequested ? PbpRiderTable({
        fram: this.props.entry.fram
      }) : d.div({}, ""))));
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
        error: (function(_this) {
          return function() {
            return console.log("it failed");
          };
        })(this),
        type: "POST"
      });
    },
    render: function() {
      window.riders = this.state.riders;
      return d.div({
        className: "row"
      }, d.div({}, d.div({
        className: "col-md-3"
      }, d.div({
        className: "well"
      }, d.p({}, "Hi there! Please email me at rjames86@gmail.com if you have any feedback or want to add a rider."), d.p({}, "Thanks!"), d.p({}, "-Ryan")))), d.div({
        className: "col-md-6"
      }, d.input({
        placeholder: "Search rider name...",
        onChange: (function(_this) {
          return function(e) {
            return _this.setState({
              filterBy: e.target.value
            });
          };
        })(this)
      }, ""), d.div({
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
      }))));
    }
  });

  $(function() {
    return React.render(LoadRiders({}), document.getElementById('react'));
  });

}).call(this);
