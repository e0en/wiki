window.onload = function() {
  const back_button = document.getElementById('back-button')

  back_button.addEventListener('click', event => {
    event.preventDefault()
    history.back()
  })

  renderMathInElement(document.body, {'delimiters': [
    {left: "$$", right: "$$", display: true},
    {left: "$", right: "$", display: false},
  ]})

}
