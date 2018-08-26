window.onload = function() {
    var content = document.getElementById("content");
    var count = document.getElementById("count");

    var display_char_count = function() {
        var n_char = content.value.length;
	count.innerHTML = String(n_char);
    };
    display_char_count();
};
