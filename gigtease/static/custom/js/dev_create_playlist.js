$("#reset-view-button").click(function () {

    let task_id = spotify_task_id
    $.post("/reset-create-playlist-tasks/",
        {'task_id': task_id},
        function (data, status) {
            window.location.reload();
        }
    )

});
