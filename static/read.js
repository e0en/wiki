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
    $(document).bind('keyup', 'n', go_next);
    $(document).bind('keyup', 'p', go_prev);
    $(document).bind('keyup', 'a', go_rand);
    $(document).bind('keyup', 'j', go_jrnl);
    $(document).bind('keyup', 'e', go_edit);
};
var unbind_all = function() {
    $(document).unbind('keyup', 'n', go_next);
    $(document).unbind('keyup', 'p', go_prev);
    $(document).unbind('keyup', 'a', go_rand);
    $(document).unbind('keyup', 'j', go_jrnl);
    $(document).unbind('keyup', 'e', go_edit);
};
window.onload = function() {
    var m = document.getElementsByTagName("meta");
    var articleURI = '';
    for(i=0; i < m.length; i++) {
        if(m[i].name == 'articleuri') {
            articleURI = m[i].content;
            break;
        }
    }
    content = document.getElementById("content");
    /*content.ondblclick = function() {
        window.location = "../edit/" + articleURI;
    };*/

    bind_all();
    $("#search_query").focus(function(){unbind_all()});
    $("#search_query").blur(function(){bind_all()});
};
