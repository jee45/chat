/**
 * Created by ad on 4/22/16.
 */

$(document).ready(function() {
    var a = io();

    var statusDisplay = $("#status");
    //var waiting = statusDisplay.attr("data-waiting");
    var waiting = true;
    var myTurnWillBe = null;

    var o = $(".chatwindow");


    var t = o.attr("data-key");
    var s = o.attr("data-sid");


    $(".join-form").on("submit", function (n) {
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


    $(".chat-input").on("submit", function (n) {
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




    a.on("connect", function () {
        console.log("connected");

        var n = o.attr("data-nick");

        if (n) {
            console.log("re-joining room %s", t);


            a.emit("enterchat", {
                sid: s,
                room: t,
                name: n
            });

        }
    });


    a.on("joined", function (n) {
        console.log(n);
        var e = n.name;
        console.log("joined %s as %s", t, e);
        o.attr("data-nick", e);
        o.addClass("joined");
        o.removeClass("unjoined")
    });


    a.on("new-chat", function (n) {
        console.log('enterying new chat');
        $("<li>").addClass("message").addClass("mid").append($("<span>").addClass("user").text(n.sender)).append(": ").append($("<span>").addClass("text").text(n.message)).prependTo($(".chat-messages"))


    });


    a.on("user-joined", function (n) {
        $("<li>").addClass("joined").append($("<span>").addClass("user").text(n.name)).append(" has joined the chat").appendTo($(".chat-messages"));
        $("<li>").text(n.name).appendTo($(".roster-list"))
    });



    /* a game board is a 3x3 array */

    var board = [
        [null, null, null, null, null, null],
        [null, null, null, null, null, null],
        [null, null, null, null, null, null],

        [null, null, null, null, null, null],
        [null, null, null, null, null, null],
        [null, null, null, null, null, null]
    ];

    var turn = null;
    //var turn = 'X';

    var winner = null;

    function getBottomOfColumn(row, col) {

        for (var i = 5; i > -1; i--) {
            console.log(board[i][col]);

            if (board[i][col] == null) {

                return i;

            }

        }
        return col;
    }


    /** Update the state of a particular cell. */
    function update(row, col, x_or_o) {


        board[row][col] = x_or_o;
        //board[bottomRow][col] = x_or_o;
        console.log(" >>>>>>>>  >>>>>>>> marking new square ", row, col);
        // update the cell's visible state


        console.log("attempting to submitMove")


        $('#cell-' + row + '-' + col).text(x_or_o).removeClass('empty').addClass(x_or_o.toLowerCase());
        //$('#cell-' + bottomRow + '-' + col).text(x_or_o).removeClass('empty').addClass(x_or_o.toLowerCase());


    }



    function changePlayer() {


        console.log('switching player.,.')

        var next;
        switch (turn) {
            case 'X':
                next = 'O';
                break;
            case 'O':
                next = 'X';
                break;
            default:
                if (winner === null) {
                    next = 'X';
                } else {
                    next = null;
                }
        }
        turn = next;

        if (next) {

            if(next==myTurnWillBe){
                // update the status!
                console.log('player %s turn', turn);
                $('#status').text('Player ' + turn + ', it is your turn!');
                waiting = false;


            }else{
                console.log('player %s turn', turn);
                $('#status').text('Player ' + turn + ', waiting for them to play.');
                waiting = true;
            }


        } else {
            $('#status').text('Game over.');
        }
    }


    function checkWinner() {
        var status;
        var empties = 0;
        var i, j;

        // count empties
        for (i = 0; i < 5; i++) {
            for (j = 0; j < 5; j++) {
                if (board[i][j] === null) {
                    empties += 1;
                }
            }
        }


        //rows cols diags
        for (i = 1; i < 5; i++) {

            for (j = 1; j < 5; j++) {


                if (board[i][j] && board[i][j] === board[i - 1][j - 1] && board[i][j] === board[i + 1][j + 1]) {
                    console.log('sloping down and right')

                    status = {
                        winner: board[i][j],
                        rows: [i - 1, i, i + 1],
                        cols: [j - 1, j, j + 1]
                    };


                } else if (board[i][j] && board[i][j] === board[i - 1][j + 1] && board[i][j] === board[i + 1][j - 1]) {
                    console.log('sloping down and left')
                    status = {
                        winner: board[i][j],
                        rows: [i - 1, i, i + 1],
                        cols: [j + 1, j, j - 1]
                    };


                } else if (board[i][j] && board[i][j] === board[i - 1][j] && board[i][j] === board[i + 1][j]) {
                    console.log('up and down')

                    status = {
                        winner: board[i][j],
                        rows: [i - 1, i, i + 1],
                        cols: [j, j, j]
                    };

                } else if (board[i][j] && board[i][j] === board[i][j - 1] && board[i][j] === board[i][j + 1]) {
                    console.log('side ways')

                    status = {
                        winner: board[i][j],
                        rows: [i, i, i],
                        cols: [j - 1, j, j + 1]
                    };

                }


            }
        }

        //edges
        for (i = 0; i < 4; i++) {

            if (board[0][i] && board[0][i] === board[0][i + 1] && board[0][i] === board[0][i + 2]) {

                console.log('top edge')
                status = {
                    winner: board[0][i],
                    rows: [0, 0, 0],
                    cols: [i, i + 1, i + 2]
                };


            } else if (board[5][i] && board[5][i] === board[5][i + 1] && board[5][i] === board[5][i + 2]) {
                console.log('bottom edge')
                status = {
                    winner: board[5][i],
                    rows: [5, 5, 5],
                    cols: [i, i + 1, i + 2]
                };


            } else if (board[i][0] && board[i][0] === board[i + 1][0] && board[i][0] === board[i + 2][0]) {


                console.log('left edge')

                status = {
                    winner: board[i][0],
                    rows: [i, i + 1, i + 2],
                    cols: [0, 0, 0]
                };


            } else if (board[i][5] && board[i][5] === board[i + 1][5] && board[i][5] === board[i + 2][5]) {
                console.log('right edge')
                status = {
                    winner: board[i][5],
                    rows: [i, i + 1, i + 2],
                    cols: [5, 5, 5]
                };


            }

        }


        if (status) {
            // we have a winner
            return status;
        } else if (empties) {
            // game still goes
            return null;
        } else {
            // no empties, no winner, game over
            return {
                winner: 'draw'
            };
        }


    }


    // game over
    function finishGame() {
        waiting=true;

        if (winner.winner === 'draw') {
            $('#status').text('The game ends in a draw.');
        } else {
            $('#status').text('Player ' + winner.winner + ' has won!');
            // now we need to mark!
            for (var i = 0; i < 5; i++) {
                var col = winner.cols[i];
                var row = winner.rows[i];
                var id = '#cell-' + row + '-' + col;
                $(id).addClass('winning');
            }
        }

        offerRematch();
    }


    function offerRematch(){
        console.log("rematch")
        $("<button>").addClass("rematch").text('rematch?').prependTo($('#status'))
        $(".rematch").on('click', acceptRematch);
        $("<button>").addClass("dontrematch").text(' dont rematch?').prependTo($('#status'))
        $(".dontrematch").on('click', dontrematch);

    }

    function dontrematch(){
        $('#status').text('you have chosen NOT to rematch.');
        a.emit('dontrematch', {'turn':turn});

    }



    function acceptRematch(){
        console.log('rematch !!!!!!!!!!!!!!!!!!');

        $(".rematch").remove();
        $('#status').text('you have accepted chosen to rematch. waiting fo opponenet to accept rematch');

        a.emit('rematchaccepted',{'turn':myTurnWillBe});



    }




    function resetGameboard(){
        for (var i = 0; i < 6; i++){
            for (var j = 0; j < 6; j++){
                $('#cell-' + i + '-' + j).text('').removeClass('x').removeClass('o').removeClass('winning');
;
                board[i][j] = null;
            }
        }
        waiting = true;

    }




    a.on("otherplayeracceptedrematch", function (d) {
        console.log("otherplayeracceptedrematch");
        resetGameboard();
        changePlayer();
    });



    a.on("anotherplayerentered", function (data) {
        console.log("anotherplayerentered");
        console.log(data);

        resetGameboard();
        myTurnWillBe = data.myTurnWillBe;
        changePlayer();


    });




    a.on("otherplayermademove", function (d) {
        console.log("otherplayermademove");
        console.log(d);
        if(waiting) {
            makeMove(d.row, d.col)
        }

    });

    a.on("someoneleftaroom", function () {
        console.log("someoneleftaroom");

    });

    function backHome(){
        window.location.assign("/")
    }

    a.on("playersleftgame", function () {
        $('#status').text('players left the room. the game is over.this room is dead. redirecting you to "/"');

        setTimeout(backHome, 5000);

    });

    a.on("observing", function (d) {
        console.log("observing");
        console.log(d);
        if(d.getNewPlayer){
            console.log("offering to enter match. ");

            $("<button>").addClass("newchallenger").text('want to play?').prependTo($('#status'))
            $(".newchallenger").on('click', newchallenger);

        }else{
            waiting=true;
            turn = d.turn
            makeMove(d.row, d.col);
            $('#status').text('you are only observing. it is Player ' + turn + ' turn.');
        }

    });

    a.on('resetGameboard', resetGameboard);

    function newchallenger(){
        console.log("trying to be the new challenger. ");
        a.emit('newchallenger');
    }


    function makeMove(row, col) {


        bottomRow = getBottomOfColumn(row, col);

        if (waiting) {
            update(bottomRow, col, turn);
            winner = checkWinner();
            if (winner) {
                finishGame();
            } else {
                changePlayer();
            }


        } else if (board[bottomRow][col] === null) {

            console.log("attempting to submit")

            a.emit("submitmove", {
                row: bottomRow,
                col: col,
                turn: turn
            });


            update(bottomRow, col, turn);
            winner = checkWinner();
            if (winner) {
                finishGame();
            } else {
                changePlayer();
            }

        } else {
            // oops - the user clicked an already-used cell
            console.log('received click in already-played cell (%d,%d)', row, col);
        }
    }





    $('.cell').on('click', function () {

        if(!waiting ) {

            var row = parseInt($(this).parent().attr('data-row'));
            var col = parseInt($(this).attr('data-col'));

            makeMove(row, col);
        }else{
            console.log('cant play yet, waiting for ther player. ');
        }



    });


});