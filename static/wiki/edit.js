window.onload = function() {
    var content = document.getElementById("content");
    var count = document.getElementById("count");
    
    content.onkeyup = function() {
        var n_char = content.value.length;
	count.innerHTML = String(n_char);
    };
};

/* 2010.02.04: full-preview functionality is disabled
// cross-browsing code for XMLHttpRequest
function getHTTPObject() {
    if(window.ActiveXObject) {
        var waystation = new ActiveXObject("Microsoft.XMLHTTP");
    }
    else if(window.XMLHttpRequest) {
        var waystation = new XMLHttpRequest();
    }
    else {
        var waystation = false;
    }
    return waystation;
    
}

window.onload = function() {
    var m = document.getElementsByTagName("meta");
    var articleURI = '';
    for(i=0; i < m.length; i++) {
        if(m[i].name == 'articleuri') {
            articleURI = m[i].content;
            break;
        }
    }

    var content = document.getElementById("content");
    var preview = document.getElementById("preview");
    
    var time_to_refresh = 3000;
    var did_change = false;
    var timer = null;
    var req = getHTTPObject();
    
    var refreshPreview = function() {
         var updatePreview = function() {
            if(req.readyState == 4) {
                preview.innerHTML = req.responseText;
            }
        };

        addr = '../preview/' + articleURI;
        req.open("POST", '../preview/' + articleURI, true);
        req.send('content=' + content.value.replace('+', '%2B'));
        req.onreadystatechange = updatePreview;
    };

    var applyChange = function() {
        if(did_change) {
            refreshPreview();
            did_change = false;
            clearTimeout(timer);
            timer = setTimeout(applyChange, time_to_refresh);
        }
        else
            return false;
    };
    
    var content_old = content.value;
    content.onkeyup = function() {
        timer = setTimeout(applyChange, time_to_refresh);
        if(this.value != content_old) {
            did_change = true;
            content_old = this.value;
        }
    };
    refreshPreview();
};
*/
