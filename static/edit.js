window.onload = function() {
  const content = document.getElementById('content');
  var count = document.getElementById('count');

  function update_content_field() {
    const n_char = content.value.length
    count.innerHTML = String(n_char)
    content.style.height = ''
    const height = content.scrollHeight;
    content.style.height = height + 'px';
    content.style.maxHeight = height + 'px';

  };
  update_content_field();

  content.addEventListener('input', event => {
    update_content_field();
  });
};
