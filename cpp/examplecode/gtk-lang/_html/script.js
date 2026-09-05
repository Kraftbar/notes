// TODO
//   - lower / capital
//   - switch input / output 


var c = document.getElementById("myCanvas");
var ctx = c.getContext("2d");
ctx.font = "30px Arial";
ctx.fillText("Hello World", 10, 50);


// globals 

var words = new Array(1000);
var words_buffer = new Array(1000);
var words_pinyin_woAccents = new Array(1000);
var words_empt=words;
var words_length=0;
correct_flag=0;
standardLang_flag=1;

// -----------------------
// file/ txts handeling 
// -----------------------




function pros(csv){
    //reset
    k=0;
    words=words_empt;

    // remove trailing newline 

    csv=csv.replace(/\n+$/, "");

    var rows = csv.split('\n');



    for (var i = 0; i < rows.length; i++) {
      cols = rows[i].split('\t');
      words[i] = new Array(3);
      for (var j = 0; j < cols.length; j++) {
        var value = cols[j];
        console.log(value)
        words[i][j] = value;
      }
      woAccents=cols[1].normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      words_pinyin_woAccents[i]=woAccents;
      words_length=i;
    }
    document.getElementById('output').innerHTML = words[k][0]+" "+words[k][1];
    
}


function processFile(){
    var file = document.querySelector('#myFile').files[0];
    var reader = new FileReader();
    reader.readAsText(file);
    reader.onload = function(event) {
      var csv = event.target.result;
      pros(csv)

    }
  }

function processText(){
    var x = document.getElementById("myTextarea").value;
    pros(x)
}


// Feedback correct 
function prossFeedback(userInput, solutions){
  highestMatchScores=[];
  feedbacks=[];

  for (j = 0; j < solutions.length; j++) {

    solution=solutions[j];

    matchScore=0;
    var feedback="";

    for (var i = 0; i < solution.length; i++) {
      if(userInput.charAt(i)==solution.charAt(i)){
        matchScore=matchScore+1;
        feedback=feedback.concat(userInput.charAt(i));
      }else{
        feedback=feedback.concat("_");
      }
    }

    feedbacks.push(feedback);
    highestMatchScores.push(matchScore);
  }

  // find the highest match
  var sorted = [...highestMatchScores].sort((a,b) => b - a);
  highestMatchIndex=highestMatchScores.indexOf(sorted[0]);

  return feedbacks[highestMatchIndex];
}

// -----------------------
// display word array 
// -----------------------



function nextItem() {
    document.getElementById('feedback').innerHTML="<br/>";
    
    k = k + 1; 
    k = k % words_length; 

    var inputF = document.getElementById("typed_word"); 
    inputF.value = ""; 

    return  words[k][0]+" "+words[k][1];
}
function prevItem() {
    document.getElementById('feedback').innerHTML="<br/>";


    if (k === 0) { // i would become 0
        k = words_length; // so put it at the other end of the array
    }
    k = k - 1; // decrease by one
    
    var inputF = document.getElementById("typed_word"); 
    inputF.value = ""; 

    return words[k][0]+" "+words[k][1]; // give us back the item of where we are now
}
function checkItem() {

  var inputVal = document.getElementById("typed_word").value;
  var answer=words[k][2].replace(/ *\([^)]*\) */g, ""); //   replace (*)
  var answers=answer.split(", ");

  feedback=prossFeedback(inputVal,answers);
    if(inputVal==feedback){              
      correct_flag=correct_flag+1;
      return feedback.concat(" ✓");
    }
      correct_flag=0;
  
    return  feedback.concat(" ☓");
}


// button input
window.addEventListener('load', function () {

    document.getElementById('prev_button').addEventListener(
        'click', // we want to listen for a click
        function (e) { // the e here is the event itself
            document.getElementById('output').textContent = prevItem();
        }
    );
    
    document.getElementById('next_button').addEventListener(
        'click', // we want to listen for a click
        function (e) { // the e here is the event itself
            document.getElementById('output').textContent = nextItem();
        }
    );
    document.getElementById('check_button').addEventListener(
        'click', // we want to listen for a click
        function (e) { // the e here is the event itself
            document.getElementById('feedback').textContent=checkItem();
        }
    );



});


// enter input
var typed_word = document.getElementById("typed_word");

typed_word.addEventListener("keyup", function(event) {
  if (event.keyCode === 13) {
    event.preventDefault();
    document.getElementById('feedback').textContent=checkItem();
    console.log(correct_flag);
    if(correct_flag>1){
      document.getElementById('output').textContent = nextItem();
    }

    }
    
});



// -----------------------
// Misc. 
// -----------------------


function changeLangFunction() {

    words=words_empt;

    for (var i = 0; i < words_length; i++) {
        if(standardLang_flag){
        words_buffer[i]=words[i][1];
        words[i][1]="";

        }else{

        words[i][1]=words_buffer[i];
        }
        [words[i][0], words[i][2]] = [words[i][2], words[i][0]];

    }


    // toggle boolean
    standardLang_flag=!standardLang_flag;

}


// -----------------------
// focus mode 
// todo: refactor, looks ugly now
// -----------------------

function focusFunction() {
    var hide0 = document.getElementById("myCanvas");

    var hide1 = document.getElementById("fileLabel");
    var hide2 = document.getElementById("myFile");
    var hide3 = document.getElementById("prosFileButton");
    var hide4 = document.getElementById("prosLabel");
    var hide5 = document.getElementById("prosButton");
    var hide6 = document.getElementById("myTextarea");
    if (hide0.style.display == "none") {
        hide0.style.display = "block";
      } else {
        hide0.style.display = "none";
      }
  
    if (hide1.style.display == "none") {
      hide1.style.display = "block";
    } else {
      hide1.style.display = "none";
    }
    
    if (hide2.style.display == "none") {
        hide2.style.display = "block";
      } else {
        hide2.style.display = "none";
      }
      
      if (hide3.style.display == "none") {
        hide3.style.display = "block";
      } else {
        hide3.style.display = "none";
      }
      if (hide4.style.display == "none") {
        hide4.style.display = "block";
      } else {
        hide4.style.display = "none";
      }
      if (hide5.style.display == "none") {
        hide5.style.display = "block";
      } else {
        hide5.style.display = "none";
      }
      if (hide6.style.display == "none") {
        hide6.style.display = "block";
      } else {
        hide6.style.display = "none";
      }
      var alignValue = "center";

      var div1 = document.getElementById ("input_output");
      var div2 = document.getElementById ("buttons");
      div1.style.textAlign = "center";
      div2.style.textAlign = "center";

  }
