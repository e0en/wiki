window.onload = function() {
  const count = document.getElementById('count')
  const content = document.getElementById('content')
  const preview_button = document.getElementById('preview-button')

  const hiddenForm = document.createElement('form')
  hiddenForm.style.display = 'none'
  hiddenForm.method = 'POST'
  const hiddenText = document.createElement('textarea')
  hiddenText.name = 'content'
  hiddenForm.appendChild(hiddenText)
  document.body.appendChild(hiddenForm)

  function update_content_field() {
    const n_char = content.value.length
    count.innerHTML = String(n_char)
  }

  preview_button.addEventListener('click', event => {
    event.preventDefault()
    const url = preview_button.href
    hiddenForm.action = url
    txt = hiddenForm.getElementsByTagName('textarea')[0]
    txt.value = content.value
    hiddenForm.submit()
  })
}
