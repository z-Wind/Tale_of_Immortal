const num_square = 13*12
// 建立 grid
var htmlElements = "";
for (var i = 0; i < num_square; i++) {
   htmlElements += '<div class="square" id=' + i + '></div>';
}
var container = document.getElementById("container");
container.innerHTML = htmlElements;


const square = document.querySelectorAll('.square')
const mole = document.querySelectorAll('.mole')
const timeLeft = document.querySelector('#time-left')
const timeInterval = document.querySelector('#time-interval')
const timeAverage = document.querySelector('#time-average')
const cpsInterval = document.querySelector('#cps-interval')
const cpsAverage = document.querySelector('#cps-average')
let score = document.querySelector('#score')
let error = document.querySelector('#error')

let totalCount = 0
let totalTime = 0
let startTime = null
let endTime = null
let result = 0
let errResult = 0
let currentTime = timeLeft.textContent

function removeFrog(){
  square.forEach(className => {
    className.classList.remove('mole')
  })
}

function randomSquare() {
  removeFrog()
  let randomPosition = square[Math.floor(Math.random() * num_square)]
  randomPosition.classList.add('mole')

  //assign the id of the randomPosition to hitPosition for us to use later
  hitPosition = randomPosition.id

  startTime = window.performance.now()
}

randomSquare()

square.forEach(id => {
  id.addEventListener('mouseup', () => {
    if(id.id === hitPosition){
      result = result + 1
      score.textContent = result
      hitPosition=null
      id.classList.remove('mole')
      if(currentTime === 0 ) {
        return
      }

      endTime = window.performance.now()
      clickTimeInterval = endTime - startTime
      timeInterval.textContent = ` ${clickTimeInterval.toFixed(2)} ms`
      cpsInterval.textContent = ` ${(1000/clickTimeInterval).toFixed(2)}`
      totalTime += clickTimeInterval
      totalCount++
      timeAverage.textContent = ` ${(totalTime/totalCount).toFixed(2)} ms`
      cpsAverage.textContent = ` ${(1000/(totalTime/totalCount)).toFixed(2)}`
      randomSquare()
    }
    else{
      errResult = errResult + 1
      error.textContent = errResult
    }
  })
})


// let timerId_random = null
// function moveMole() {
//   timerId_random = setInterval(randomSquare, 50)
// }

// moveMole()


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