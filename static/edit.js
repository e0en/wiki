window.onload = function() {
  const count = document.getElementById('count')
  const content = document.getElementById('content')
  const preview_button = document.getElementById('preview-button')

  function update_content_field() {
    const n_char = content.value.length
    count.innerHTML = String(n_char)
  }

  preview_button.addEventListener('click', event => {
    event.preventDefault()
    const url = preview_button.href

    const form = document.createElement('form')
    form.method = 'POST'
    form.style.diplay = 'none'
    form.action = url
    const hidden = document.createElement('textarea')
    hidden.name = 'content'
    hidden.id = 'preview-content'
    hidden.value = content.value
    hidden.style.diplay = 'none'
    form.appendChild(hidden)
    document.body.appendChild(form)
    form.submit()
  })
}
