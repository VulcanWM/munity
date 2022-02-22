var Script1 = document.createElement("script");
Script1.setAttribute("async", null);
Script1.src = 
"https://www.googletagmanager.com/gtag/js?id=G-X6E94CWWDF";
document.head.appendChild(Script1);


var Script2 = document.createElement("script");
Script2.innerText = 
"window.dataLayer = window.dataLayer || [];function gtag(){dataLayer.push(arguments);}gtag('js', new Date());gtag('config', 'G-X6E94CWWDF');";
document.head.appendChild(Script2);

// window.onscroll = function() {myFunction()};

var navbar = document.getElementById("navbar");
// var sticky = navbar.offsetTop;

// function myFunction() {
//   if (window.pageYOffset >= sticky) {
//     navbar.classList.add("sticky")
//   } else {
//     navbar.classList.remove("sticky");
//   }
// }

function openCity(evt, cityName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(cityName).style.display = "block";
  evt.currentTarget.className += " active";
}

document.getElementById("defaultOpen").click();

function navbaredit(thelist){
  const elements = {
    home : '<a class="nav-link nav-link-ltr" href="/">Home</a>',
    setartist  : '<a class="nav-link nav-link-ltr" href="/setartist">set artist</a>',
    changeartist: '<a class="nav-link nav-link-ltr" href="/setartist">change artist</a>',
    guesssong     : '<a class="nav-link nav-link-ltr" href="/guesssong">guess lyrics</a>',
    guessalbum  : '<a class="nav-link nav-link-ltr" href="/guessalbum">guess album</a>',
    login: '<a class="nav-link nav-link-ltr" href="/login">Login</a>',
    signup: '<a class="nav-link nav-link-ltr" href="/signup">Signup</a>',
    leaderboard: '<a class="nav-link nav-link-ltr" href="/leaderboard">Leaderboard</a>',
    profile: '<a class="nav-link nav-link-ltr" href="/profile">Profile</a>',
    logout: '<a class="nav-link nav-link-ltr" href="/logout">Logout</a>'
  };
  var thenavbar = document.getElementsByClassName("navbar")[0]
  for (let i = 0; i < thelist.length; i++) {
    thenavbar.innerHTML = thenavbar.innerHTML + elements[thelist[i]];
  }
}