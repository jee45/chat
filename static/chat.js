/**
 * Created by ad on 4/22/16.
 */
(function(n, e) {
    //var a = io();


    var o = $(".chatwindow");



    var t = o.attr("data-key");
    var s = o.attr("data-sid");

    var a = io();




    $(".join-form").on("submit", function(n) {
        n.preventDefault();
        var e = $("#join-nick").val();
        if (e) {
            console.log("joining room %s as %s", t, e);
            a.emit("enterchat", {
                sid: s,
                room: t,
                name: e
            });

            console.log("tried to join")

        }

    });






    $(".chat-input").on("submit", function(n) {
        n.preventDefault();
        var e = $("#in-msg").val().trim();
        if (!e)
            return;
        console.log("submitting message");
        a.emit("chat", {
            sid: s,
            room: t,
            message: e
        });

        $("#in-msg").val("")
    });





    a.on("connect", function() {
        console.log("connected");

        var n = o.attr("data-nick");

        if (n) {

            console.log("re-joining room %s", t);
            a.emit("enterchat", {
                sid: s,
                room: t,
                name: n
            })

        }
    });





    a.on("joined", function(n) {
        console.log(n);
        var e = n.name;
        console.log("joined %s as %s", t, e);
        o.attr("data-nick", e);
        o.addClass("joined");
        o.removeClass("unjoined")
    });









    a.on("new-chat", function(n) {
        console.log('enterying new chat');
        $("<li>").addClass("message").append($("<span>").addClass("user").text(n.sender)).append(": ").append($("<span>").addClass("text").text(n.message)).appendTo($(".chat-messages"))


    });




    a.on("user-joined", function(n) {
        $("<li>").addClass("joined").append($("<span>").addClass("user").text(n.name)).append(" has joined the chat").appendTo($(".chat-messages"));
        $("<li>").text(n.name).appendTo($(".roster-list"))
    });




    e[""] = n
})({}, function() {
    return this
}());