const square = document.querySelectorAll('.square')
const mole = document.querySelectorAll('.mole')
const timeLeft = document.querySelector('#time-left')
let score = document.querySelector('#score')

let result = 0
let currentTime = timeLeft.textContent

function removeFrog(){
  square.forEach(className => {
    className.classList.remove('mole')
  })
}

function randomSquare() {
  removeFrog()
  let randomPosition = square[Math.floor(Math.random() * 100)]
  randomPosition.classList.add('mole')

  //assign the id of the randomPosition to hitPosition for us to use later
  hitPosition = randomPosition.id
}

square.forEach(id => {
  id.addEventListener('mouseup', () => {
    if(id.id === hitPosition){
      result = result + 1
      score.textContent = result
      hitPosition=null
      id.classList.remove('mole')
    }
  })
})


let timerId_random = null
function moveMole() {
  timerId_random = setInterval(randomSquare, 50)
}

moveMole()


function countDown() {
  currentTime--
  timeLeft.textContent = currentTime

  if(currentTime === 0 ) {
    removeFrog()
    clearInterval(timerId)
    clearInterval(timerId_random)
    //alert('GAME OVER! Your final score is' + result)
  }
}

let timerId = setInterval(countDown, 1000)
