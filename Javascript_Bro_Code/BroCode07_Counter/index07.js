
const btnDecrease = document.getElementById("btnDecrease");
const btnIncrease = document.getElementById("btnIncrease");
const btnReset = document.getElementById("btnReset");
const lblCount = document.getElementById("lblCount");
let count = 0;

btnDecrease.onclick = function(){
    count--;
    lblCount.textContent = count;
}
btnIncrease.onclick = function(){
    count++;
    lblCount.textContent = count;
}
btnReset.onclick = function(){
    count = 0;
    lblCount.textContent = count;
}