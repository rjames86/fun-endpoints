d = React.DOM

root = exports ? this

spData = null

root.doData = (json) ->
  spData = json.feed.entry
  return

drawCell = (tr, val) ->
  td = $('<td/>')
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
  i: 0
  start: undefined

  getInitialState: ->
    checkPoints: [
      "START",
      "MORTAGNE",
      "VILLAINES",
      "FOUGERES",
      "TINTENIAC",
      "LOUDEAC",
      "CARHAIX",
      "BREST",
      "CARHAIX",
      "LOUDEAC",
      "TINTENIAC",
      "FOUGERES",
      "VILLAINES",
      "MORTAGNE",
      "DREUX",
      "FINISH"
    ]
    data: null

  componentDidMount: ->
    $.ajax({
          url: 'http://suivi.paris-brest-paris.org/data/' + @props.fram + '.txt',
          success: (strData) =>
            temps = strdata.split(';')
            # aff_resultat(temps)
            if @isMounted
              @setState data: temps
          error: =>
            if @isMounted
              @setState data: []
            return
          type: "GET",
          async: false,
          cache: true,
          crossDomain: true,
          dataType: 'jsonp'
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

  aff_heure: ->
    aff = conv_heure(conv_min(@state.data[@i]) - @start)
    aff

  aff_date:  ->
    if @state.data[@i] != ''
      #Start ini: 16/08 16:00
      d = 16
      t = conv_min(@state.data[@i]) + conv_min('16:00')
      while t > 1440
        t = t - 1440
        d++
      i++
      d + '/08 ' + conv_heure(t)
    else
      ''

  makeRow: (location) ->
    d.tr {},
      d.td {}, location
      d.td {}, @aff_heure @state.data
      if location == 'FINISH'
        if @state.data[17] == '' or @state.data[17] == 'OK'
          d.td {}, @aff_date(@state.data)
        else if @state.data[17] == 'AB'
          d.td {}, "Abandon"
        else if @state.data[17] == 'NP'
          d.td {}, "Non Partant"
      else
        d.td {}, @aff_date

  render: ->
    console.log "data", @state.data
    if @state.data == null
      d.p {}, "loading..."
    else if @state.data.length
      @start = conv_min(@state.data[0])
      table = (d.table {border: 1},
        d.tr {},
          d.td {width: '100'}, "Contrôle"
          d.td {width: '100'}, "Temps"
          d.td {width: '150'}, "Passage"
        @state.checkPoints.map (location) -> @makeRow location)
      @i = 0
      return table
    else
      d.p {}, "no results :("

Accordian = React.createClass
  getInitialState: ->
    loadRequested: false
    previousClick: null

  onClick: ->
    $("[class~=collapse]").collapse("hide");
    $("#collapse-#{@props.entry.Fram}").collapse('toggle');
    @setState loadRequested: true

  makeHeader: ->
    d.h4 {className: "panel-title"},
      d.a {
        "data-toggle": "collapse",
        "data-parent": "#accordian",
        # href: "#collapse-#{@props.entry.Fram}"
        onClick: => @onClick()
      }, "#{@props.entry.First} #{@props.entry.Last}"

  render: ->
    d.div {className: "panel panel-default"},
      d.div {className: "panel-heading"},
        @makeHeader()
      d.div {id:"collapse-#{@props.entry.Fram}", className: "panel-collapse collapse"},
        d.div {className: "panel-body"},
          d.div {className: "well"},
            d.p {}, "Start: #{@props.entry.Wave}"
            d.p {}, "Group: #{@props.entry['Club Name']}"
          if @state.loadRequested
            PbpRiderTable fram: @props.entry.Fram
          else
            d.div {}, ""

LoadRiders = React.createClass
  getInitialState: ->
    dataUrl: "https://spreadsheets.google.com/feeds/cells/1FAWvqlEmbUbMJgbUJndCFiU_3PSFi4kVSoa6iFtJd0A/1/public/values?alt=json-in-script&callback=doData",
    riders: []
    loadingText: "Grabbing info"

  componentDidMount: ->
    $.get @state.dataUrl, =>
      if @isMounted
        @setState riders: readData $("#data")

  loadPbpInfo: (fram) ->
    if @state[fram]
      return
    $.ajax({
          url: 'http://suivi.paris-brest-paris.org/data/' + fram + '.txt',
          success: (strData) =>
            temps = strdata.split(';')
            # aff_resultat(temps)
            newState = @state
            newState[fram] = temps
            @setState  newState
            return
          error: =>
            newState = @state
            newState[fram] = "No results"
            @setState newState
            return
          type: "GET",
          async: false,
          cache: true,
          crossDomain: true,
          dataType: 'jsonp'
      })

  render: ->
    d.div {className: "panel-group", id:"accordian"},
      @state.riders.map (entry) => Accordian entry: entry


$ ->
  React.render LoadRiders({}), document.getElementById('react')

