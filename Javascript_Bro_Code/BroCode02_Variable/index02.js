// https://www.youtube.com/watch?v=lfmg-EJ8gm4&list=WL&index=12&t=23655s
/* 
Variables
*/

let x;
let y;

x = 100;

console.log(x);

let age = 25;

console.log(age);
console.log(`You are ${age}`);
console.log(`Give me $${25}`);

let firstName ='Ken';
console.log(typeof firstName);
console.log(`My name is ${firstName} and I am ${age}`);

// Booleans

let online = true;

// display on the webpage

let fullName = 'Ken Harmon';
let student = false;

document.getElementById('P1').textContent = `Your name: ${fullName}`;
document.getElementById('P2').textContent = `Your age: ${age}`;
document.getElementById('P3').textContent = `Enrolled: ${student}`;
