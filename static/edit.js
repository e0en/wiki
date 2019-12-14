window.onload = function() {
  var count = document.getElementById('count');

  function update_content_field() {
    const n_char = content.value.length
    count.innerHTML = String(n_char)
  };
  update_content_field();

  content.addEventListener('input', event => {
    update_content_field();
  });
};
