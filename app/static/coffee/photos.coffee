getPhotos = ->
    $.ajax
        url: 'get_photos'
        beforeSend: ->
            console.log "before send"
        success: handleResults

handleResults = (response) ->
    kvStore.set "photos", response.data
    for item in response.data
        $('body').append "<p>#{item.path}</p>"

    console.log kvStore.get("photos")[0]

d  = React.DOM

Page = React.createClass
    getInitialState: () ->
        loading: true
        thumbnail: null

    componentDidMount: ->
        @setState
            loading: false
        @getThumbnail("path")

    getThumbnail: (path) ->
        console.log "getting thumb"
        $.ajax
            url: 'thumbnail'
            data:
                path: "Pictures/Picture a Day/2013-05-30.jpg"
            success: (response) =>
                if @isMounted()
                    @setState
                        thumbnail: response

    render: () ->
        console.log "hi"
        console.log @state
        d.div {}, "hello world"

$ ->
    React.render(
        Page({}),
        document.getElementById('react')
    )
