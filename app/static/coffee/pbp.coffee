d = React.DOM
i= 0
start = undefined
m1 = undefined
m2 = undefined
next = undefined

root = exports ? this

spData = null

root.doData = (json) ->
  spData = json.feed.entry
  return

drawCell: (tr, val) ->
  tdd = $('<td/>')
  tr.append td
  td.append val
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
      "MORTAGNE"
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
      140
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
    `var aff_moy`
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
      d.td {}, location
      d.td {}, @aff_km @state.data
      d.td {}, @aff_heure @state.data
    ]
    if location == 'FINISH'
      if @state.data[17] == '' or @state.data[17] == 'OK'
        rows.push (d.td {}, @aff_date(@state.data))
      else if @state.data[17] == 'AB'
        rows.push (d.td {}, "Abandon")
      else if @state.data[17] == 'NP'
        rows.push (d.td {}, "Non Partant")
    else
      rows = rows.concat [
        d.td {}, @aff_date(@state.data),
        d.td {}, @aff_moy(@state.data),
        d.td {}, @aff_moytot(@state.data),
    ]
    d.tr {},
      rows





  render: ->
    to_ret = []
    if @state.data == null
      d.p {}, "loading..."
    else if @state.data.length
      start = @conv_min(@state.data[0])
      table = (d.table {border: 1},
        d.tr {},
          d.td {width: '100'}, "Contrôle"
          d.td {width: '100'}, "KM"
          d.td {width: '100'}, "Temps"
          d.td {width: '150'}, "Passage"
          d.td {}, "Moyenne tronçon"
          d.td {}, "Moyenne Totale"
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
        extra = d.p {}, "Heure estimée d'arrivée au prochain contrôle entre #{@aff_date_min(t1)} et #{@aff_date_min(t2)}"
        to_ret.push extra
      i = 0
      return table
    else
      d.p {}, "no results :("

Accordian = React.createClass
  getInitialState: ->
    loadRequested: false
    previousClick: null

  onClick: ->
    $("[class~=collapse]").collapse("hide")
    $("#collapse-#{@props.entry.fram}").collapse('toggle')
    @setState loadRequested: true

  makeHeader: ->
    d.h4 {className: "panel-title"},
      d.a {
        "data-toggle": "collapse",
        "data-parent": "#accordian",
        # href: "#collapse-#{@props.entry.fram}"
        onClick: => @onClick()
      }, "#{@props.entry.first} #{@props.entry.last}"

  render: ->
    d.div {className: "panel panel-default"},
      d.div {className: "panel-heading"},
        @makeHeader()
      d.div {id:"collapse-#{@props.entry.fram}", className: "panel-collapse collapse"},
        d.div {className: "panel-body"},
          d.div {className: "well"},
            d.p {}, "Wave: #{@props.entry.wave}"
            d.p {}, "Start: #{@props.entry.start} hour"
            d.p {}, "Group: #{@props.entry['club_name']}"
          if @state.loadRequested
            PbpRiderTable fram: @props.entry.fram
          else
            d.div {}, ""

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
    # d.li {className: "dropdown"},
    #   d.a {className: "dropdown-toggle", "data-toggle": "dropdown", role: "button"}, "Clubs", d.span {className: "caret"}, ""
    #   d.ul {className: "dropdown-menu"},
    #     _.map uniqClubs, (club) -> d.li {}, d.a {href: "#"}, club
    d.select {className: "form-control"},
      _.map uniqClubs, (club) -> d.option {value: club}, club

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
    d.nav {className: "navbar navbar-default"},
      d.div {className: "container-fluid"},
        d.div {className: "navbar-header"},
          d.p {className: "navbar-brand"}, "PBP"
        d.div {className: "collapse navbar-collapse", id: "pbp-navbar"},
          d.ul {className: "nav navbar-nav"},
            d.li {}, d.a {href: "#"}, "Link"
            @getDropdowns()

  render: ->
    window.riders = @state.riders
    d.div {className: "col-md-12"},
    #   d.div {className: "row"},
    #     @navBar()
      d.div {className: "row"},
        d.div {},
          d.div {className: "col-md-3"},
            d.div {className: "well"},
              d.p {}, "Hi there! Please email me at rjames86@gmail.com if you have any feedback or want to add a rider."
              d.p {}, "Thanks!"
              d.p {}, "-Ryan"
            # d.form {},
            #   d.input {
            #     placeholder:"name",
            #     name:"name",
            #     onChange: (e) =>
            #       @setState name: e.target.value
            #   }, ""
            #   d.input {
            #     placeholder:"email",
            #     name:"email",
            #     onChange: (e) => @setState email: e.target.value
            #   }, ""
            #   d.input {
            #     placeholder:"rider",
            #     name:"rider_name",
            #     onChange: (e) => @setState rider_name: e.target.value
            #   }, ""
            #   d.button {onClick: @handleEmailSubmit}, "Send"
        d.div {className: "col-md-6"},
          # d.input {
          #   placeholder: "Search rider name..."
          #   className: "form-control"
          #   onChange: (e) =>
          #     @setState filterBy: e.target.value
          # }, ""
          d.div {className: "panel-group", id:"accordian"},
            if @state.filterBy.length
              @filterByName().map (entry) -> Accordian entry: entry
            else
              @state.riders.map (entry) -> Accordian entry: entry

$ ->
  React.render LoadRiders({}), document.getElementById('react')

