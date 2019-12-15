window.onload = function() {
  const count = document.getElementById('count')
  const content = document.getElementById('content')

  function update_content_field() {
    const n_char = content.value.length
    count.innerHTML = String(n_char)
  }

  content.focus()
  update_content_field()

  content.addEventListener('input', event => {
    update_content_field()
  })
};
