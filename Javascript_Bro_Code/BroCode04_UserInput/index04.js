// User Input https://www.youtube.com/watch?v=lfmg-EJ8gm4&list=WL&index=12&t=23655s

// Easy way = window Prompt

let userName;

userName = window.prompt('What is your username?');

console.log(userName);

// Professional way = HTML Textbox
document.getElementById('mySubmit').onclick = function(){
    userName = document.getElementById('myText').value;
    document.getElementById('myH1').textContent = `Hello ${userName}`
}
