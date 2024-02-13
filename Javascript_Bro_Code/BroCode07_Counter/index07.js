// Constants https://www.youtube.com/watch?v=lfmg-EJ8gm4&list=WL&index=13&t=23655s

const PI = 3.14159; 
let radius;
let circumference;





document.getElementById("mySubmit").onclick = function(){
    radius = Number(document.getElementById("myText").value);
    circumference = 2 * PI * radius;
    document.getElementById("myH3").textContent = `Circumference is ${circumference}`;
}

