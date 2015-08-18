d = React.DOM
React.initializeTouchEvents(true)

i= 0
start = undefined
m1 = undefined
m2 = undefined
next = undefined

root = exports ? this

spData = null

root.doData = (json) ->
  spData = json.feeReact.DOM.entry
  return

drawCell: (tr, val) ->
  tdd = $('<td/>')
  tr.append td
  tReact.DOM.append val
  td

drawRow = (table, rowData) ->
  if rowData == null
    return null
  if rowData.length == 0
    return null
  tr = $('<tr/>')
  table.append tr
  c = 0
  while c < rowData.length
    drawCell tr, rowData[c]
    c++
  tr

drawTable = (parent) ->
  table = $('<table/>')
  parent.append table
  table

root.readData = (parent) ->
  data = spData
  # table = drawTable(parent)
  rowData = []
  headers = []
  pbpRiderInfo = []
  r = 0
  while r < data.length
    cell = data[r]['gs$cell']
    val = cell['$t']
    if `cell.row == 1`
      headers.push val
    else if `cell.col == 1` and cell.row > 2
      pbpRiderInfo.push rowData
    if `cell.col == 1`
      # drawRow table, rowData
      rowData = []
    rowData.push val
    r++
  # drawRow table, rowData
  pbpRiderInfo.push rowData

  return _.map(pbpRiderInfo, (rider) -> _.object headers, rider)



PbpRiderTable = React.createClass
  getInitialState: ->
    checkPoints: [
      "START"
      "VILLAINES"
      "FOUGERES"
      "TINTENIAC"
      "LOUDEAC"
      "CARHAIX"
      "BREST"
      "CARHAIX"
      "LOUDEAC"
      "TINTENIAC"
      "FOUGERES"
      "VILLAINES"
      "MORTAGNE"
      "DREUX"
      "FINISH"
    ]
    km: [
      0
      221
      310
      364
      449
      525
      618
      703
      782
      867
      921
      1009
      1090
      1165
      1230
    ]
    data: null

  componentDidMount: ->
    $.ajax({
      url: '/pbp_rider_status',
      data:
        fram: @props.fram
      success: (strData) =>
        if strData.message == "Success"
          temps = strData.resp.split(';')
          # aff_resultat(temps)
          if @isMounted
            @setState data: temps
        else
          @setState data: []
      error: =>
        if @isMounted
          @setState data: []
        return
      type: "GET",
      async: false,
      cache: true,
    })

  conv_min: (temps) ->
    t = temps.split(':')
    min = parseInt(t[0] * 60) + parseInt(t[1])
    min

  conv_heure: (temps) ->
    if parseInt(temps) > 0
      h = parseInt(temps / 60)
      min = temps - (h * 60)
      if min < 10
        min = '0' + min
      if h < 10
        h = '0' + h
      h + ':' + min
    else
      ''

  aff_heure: (data) ->
    aff = @conv_heure(@conv_min(@state.data[i]) - start)
    aff

  aff_date: (data) ->
    if data[i] != ''
      #Start ini: 16/08 16:00
      dd = 16
      t = @conv_min(@state.data[i])
      while t > 1440
        t = t - 1440
        dd++
      return dd + '/08 ' + @conv_heure(t)
    else
      return ''

  aff_date_min: (min) ->
    dd = 16
    t = min
    while t > 1440
      t = t - 1440
      d++
    d + '/08 ' + @conv_heure(t)

  aff_km: (data) ->
    if data[i] != ''
      next = i
      @state.km[i]
    else
      ''

  aff_moy: (data) ->
    if data[i] != '' and i > 0
      if data[i - 1] != ''
        r = parseInt((@state.km[i] - (@state.km[i - 1])) / (@conv_min(@state.data[i]) - @conv_min(@state.data[i - 1])) * 600) / 10 + ' km/h'
        m1 = r
        return r
    ''

  aff_moytot: (data) ->
    if data[i] != '' and i > 0
      if data[i - 1] != ''
        r = parseInt(@state.km[i] / (@conv_min(@state.data[i]) - @conv_min(@state.data[0])) * 600) / 10 + ' km/h'
        i++
        m2 = r
        return r
    i++
    ''

  makeRow: (location) ->
    rows = [
      React.DOM.td {}, location
      React.DOM.td {}, @aff_km @state.data
      React.DOM.td {}, @aff_heure @state.data
    ]
    if location == 'FINISH'
      if @state.data[17] == '' or @state.data[17] == 'OK'
        rows.push (React.DOM.td {}, @aff_date(@state.data))
      else if @state.data[17] == 'AB'
        rows.push (React.DOM.td {}, "Abandon")
      else if @state.data[17] == 'NP'
        rows.push (React.DOM.td {}, "Non Partant")
    else
      rows = rows.concat [
        React.DOM.td {}, @aff_date(@state.data),
        React.DOM.td {}, @aff_moy(@state.data),
        React.DOM.td {}, @aff_moytot(@state.data),
    ]
    React.DOM.tr {},
      rows





  render: ->
    to_ret = []
    if @state.data == null
      React.DOM.p {}, "loading..."
    else if @state.data.length
      start = @conv_min(@state.data[0])
      table = (React.DOM.table {border: 1},
        React.DOM.tr {},
          React.DOM.td {width: '100'}, "Contrôle"
          React.DOM.td {width: '100'}, "KM"
          React.DOM.td {width: '100'}, "Temps"
          React.DOM.td {width: '150'}, "Passage"
          React.DOM.td {}, "Moyenne tronçon"
          React.DOM.td {}, "Moyenne Totale"
        @state.checkPoints.map (location) => @makeRow location)
      to_ret.push table
      if next == 0
        m1 = '20 km/h'
        m2 = '35 km/h'
      if next < 15
        m1 = parseInt(m1.split(' ')[0])
        m2 = parseInt(m2.split(' ')[0])
        t1 = (@state.km[next + 1] - (@state.km[next])) / m1 * 60 + @conv_min(@state.data[next])
        t2 = (@state.km[next + 1] - (@state.km[next])) / m2 * 60 + @conv_min(@state.data[next])
        if t1 > t2
          t = t1
          t1 = t2
          t2 = t
        extra = React.DOM.p {}, "Heure estimée d'arrivée au prochain contrôle entre #{@aff_date_min(t1)} et #{@aff_date_min(t2)}"
        to_ret.push extra
      i = 0
      return table
    else
      React.DOM.p {}, "no results :("

Accordian = React.createClass
  getInitialState: ->
    loadRequested: false
    previousClick: null

  onClick: ->
    $("[class~=collapse]").collapse("hide")
    $("#collapse-#{@props.entry.fram}").collapse('toggle')
    @setState loadRequested: true

  makeHeader: ->
    React.DOM.h4 {className: "panel-title"},
      React.DOM.a {
        "data-toggle": "collapse",
        "data-parent": "#accordian",
        # href: "#collapse-#{@props.entry.fram}"
        onClick: => @onClick()
        onTouchEnd: => @onClick()
      }, "#{@props.entry.first} #{@props.entry.last}"

  render: ->
    React.DOM.div {className: "panel panel-default", key: @props.entry.fram},
      React.DOM.div {className: "panel-heading"},
        @makeHeader()
      React.DOM.div {id:"collapse-#{@props.entry.fram}", className: "panel-collapse collapse"},
        React.DOM.div {className: "panel-body"},
          React.DOM.div {className: "well"},
            React.DOM.p {}, "Wave: #{@props.entry.wave}"
            React.DOM.p {}, "Start: #{@props.entry.start} hour"
            React.DOM.p {}, "Group: #{@props.entry['club_name']}"
          if @state.loadRequested
            PbpRiderTable fram: @props.entry.fram
          else
            React.DOM.div {}, ""

LoadRiders = React.createClass
  getInitialState: ->
    # dataUrl: "https://spreadsheets.google.com/feeds/cells/1FAWvqlEmbUbMJgbUJndCFiU_3PSFi4kVSoa6iFtJd0A/1/public/values?alt=json-in-script&callback=doData",
    dataUrl: "/pbp_riders",
    riders: []
    loadingText: "Grabbing info"
    filterBy: ""
    name: ""
    email: ""
    rider_info: ""

  componentDidMount: ->
    $.get @state.dataUrl, (data) =>
      if @isMounted
        @setState riders: data.data #readData $("#data")

  filterByName: ->
    _.filter(
      @state.riders,
      (entry) =>
        entry.full_name.toLowerCase().indexOf(@state.filterBy.toLowerCase()) > -1
    )

  getDropdowns: ->
    uniqClubs = _.unique _.map riders, (rider) -> return rider.club_name
    # React.DOM.li {className: "dropdown"},
    #   React.DOM.a {className: "dropdown-toggle", "data-toggle": "dropdown", role: "button"}, "Clubs", React.DOM.span {className: "caret"}, ""
    #   React.DOM.ul {className: "dropdown-menu"},
    #     _.map uniqClubs, (club) -> React.DOM.li {}, React.DOM.a {href: "#"}, club
    React.DOM.select {className: "form-control"},
      _.map uniqClubs, (club) -> React.DOM.option {value: club}, club

  handleEmailSubmit: (event) ->
    event.preventDefault()
    $.ajax({
      url: '/pbp_rider_request'
      data:
        name: @state.name
        email: @state.email
        rider_name: @state.rider_name
      success: ->
        console.log "winner"
      error: ->
        console.log "it failed"
      type: "POST",
    })

  navBar: ->
    React.DOM.nav {className: "navbar navbar-default"},
      React.DOM.div {className: "container-fluid"},
        React.DOM.div {className: "navbar-header"},
          React.DOM.p {className: "navbar-brand"}, "PBP"
        React.DOM.div {className: "collapse navbar-collapse", id: "pbp-navbar"},
          React.DOM.ul {className: "nav navbar-nav"},
            React.DOM.li {}, React.DOM.a {href: "#"}, "Link"
            @getDropdowns()

  render: ->
    window.riders = @state.riders
    React.DOM.div {className: "col-md-12"},
    #   React.DOM.div {className: "row"},
    #     @navBar()
      React.DOM.div {className: "row"},
        React.DOM.div {},
          React.DOM.div {className: "col-md-3 col-xs-12 col-s-12"},
            React.DOM.div {className: "well"},
              React.DOM.p {}, "Hi there! Please email me at rjames86@gmail.com if you have any feedback or want to add a rider."
              React.DOM.p {}, "Thanks!"
              React.DOM.p {}, "-Ryan"
            # React.DOM.form {},
            #   React.DOM.input {
            #     placeholder:"name",
            #     name:"name",
            #     onChange: (e) =>
            #       @setState name: e.target.value
            #   }, ""
            #   React.DOM.input {
            #     placeholder:"email",
            #     name:"email",
            #     onChange: (e) => @setState email: e.target.value
            #   }, ""
            #   React.DOM.input {
            #     placeholder:"rider",
            #     name:"rider_name",
            #     onChange: (e) => @setState rider_name: e.target.value
            #   }, ""
            #   React.DOM.button {onClick: @handleEmailSubmit}, "Send"
        React.DOM.div {className: "col-md-6 col-xs-12 col-s-12"},
          # React.DOM.input {
          #   placeholder: "Search rider name..."
          #   className: "form-control"
          #   onChange: (e) =>
          #     @setState filterBy: e.target.value
          # }, ""
          React.DOM.div {className: "panel-group", id:"accordian"},
            if @state.filterBy.length
              @filterByName().map (entry) -> Accordian entry: entry
            else
              @state.riders.map (entry) -> Accordian entry: entry

$ ->
  React.render LoadRiders({}), document.getElementById('react')

