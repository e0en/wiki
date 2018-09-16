var go_next = function() {
    a_next = document.getElementById("nav_next_page");
    if(a_next != null) {
        window.location = a_next.href;// move to the a_next.href
        return false;
    }
    else
        return false;
};

var go_prev = function() {
    a_prev = document.getElementById("nav_prev_page");
    if(a_prev != null) {
        window.location = a_prev.href;// move to the a_prev.href
        return false;
    }
    else
        return false;
};

var go_rand = function() {
    window.location = '../random';
};

var go_jrnl = function() {
    window.location = '../jrnl';
};

var go_edit = function() {
    window.location = document.getElementById('control_edit').href;
};

var bind_all = function() {
    document.onkeyup = function(e) {
        switch (e.key) {
            case 'p':
                go_prev();
                break;
            case 'n':
                go_next();
                break;
            case 'a':
                go_rand();
                break;
            case 'j':
                go_jrnl();
                break;
            case 'e':
                go_edit();
                break;
            default:
                return;
        }
    };
};

var unbind_all = function() {
    document.onkeyup = function(e) {};
};

window.onload = function() {
    bind_all();
    search_input = document.getElementById("search_query");
    search_input.onfocus = unbind_all;
    search_input.onblur = bind_all;

    renderMathInElement(document.body, {'delimiters': [
      {left: "$$", right: "$$", display: true},
      {left: "$", right: "$", display: false},
    ]});


    redirect = document.getElementsByClassName("redirect");
    if (redirect.length > 0) {
        redirect = redirect[0];
		function sleep(ms) {
		  return new Promise(resolve => setTimeout(resolve, ms));
		}
		sleep(2000).then(() => {
			window.location.replace(redirect.href);
		});
    }
};
