async function loadHeader() {
    document.querySelector(".head-banner").innerHTML = await ( await fetch("/header")).text();
    var menu = document.getElementsByClassName("menu-items");
    var hamburger = document.querySelector("#ham");
    var mainContent = document.querySelector(".main-content");
    hamburger.addEventListener("click", function() {
        if (hamburger.innerHTML== "\uFE3E") {
            hamburger.innerHTML = "\uFE3D";
        } else {
            hamburger.innerHTML = "\uFE3E";
        }
        mainContent.classList.toggle("blur");
        for (let i = 0; i < menu.length; i++) {
            var element = menu[i];
            element.classList.toggle("nested");
        }
    })
}
loadHeader();

// button function : done/ not done
var topicIdTextBox = document.getElementById("topic-id");
if (topicIdTextBox){
    topicIdTextBox.addEventListener("keypress", event=>{
        if (event.key == "Enter") doneTopic();
    })
}


// stats page : tree
var toggler = document.getElementsByClassName("caret");
for (let i=0; i< toggler.length; i++){    
    let item = toggler[i];
    item.addEventListener("click", function(){        
        this.parentElement.querySelector(".nested").classList.toggle("active");
        this.classList.toggle("caret-down");
    })
}

// stats page : progress
var progress_elements = document.getElementsByClassName("sub-progress");
for (let i=0; i<progress_elements.length; i++){
    let item = progress_elements[i];
    if (item.innerHTML < 50){
        item.classList.add("red");
    } else if (item.innerHTML < 80){
        item.classList.add("yellow");
    } else if (item.innerHTML <=100){
        item.classList.add("green");
    }
}

function addTopic() {
    var subjectIpput = document.getElementById("subject-name");
    var topicsInput = document.getElementById("topic-names");
    
    var subject = subjectIpput.value;
    var topics = topicsInput.value.trim().split('\n');
    
    if (subject && topics){
        var xhr = new XMLHttpRequest();
        xhr.open('POST', "/add-topics",true)
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = ()=>{
            if (xhr.readyState == 4 && xhr.status == 200){
                console.log("Added the Topic")
            }
        }
        
        json = new Array();
        topics.forEach(t => {            
            obj = new Object
            obj["subject"] = subject.toUpperCase();
            obj["topic"] = t;
            json.push(obj);            
        });

        xhr.send(JSON.stringify(json));
        
        subjectIpput.value = "";
        topicsInput.value = "";    

    } else{
        console.log("Fill the topic and subject first");
    }     
}

// function doneTopic() {
//     var topicIdTextBox = document.getElementById("topic-id");
//     var topicId = topicIdTextBox.value;
//     if (topicId){
//         var xhr = new XMLHttpRequest();
//         xhr.open('GET', "/done/"+topicId, false)
//         xhr.onreadystatechange = ()=>{
//             if (xhr.readyState == 4 && xhr.status == 200){                
//                 console.log("Done Topic")
//             }
//         }
//         xhr.send();   
//         location.reload()
//     } else {
//         console.log("Fill the topic ID (S. No.)");
//     } 
// }

function doneTopic(action, id) {    
    var xhr = new XMLHttpRequest();
    xhr.open('GET', "/"+action+"/"+id, false)
    xhr.onreadystatechange = ()=>{
        if (xhr.readyState == 4 && xhr.status == 200){                
            console.log("Done Topic")
        }
    }
    xhr.send();   
    location.reload()
}

function login() {
    var regUser = document.querySelector("#user");
    var regPassword = document.querySelector("#password");
    var user = regUser.value;
    var pass = regPassword.value;
    var t_offset = new Date().getTimezoneOffset();
    if (user && pass){
        var xhr = new XMLHttpRequest();
        xhr.open('POST', "/login", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = ()=>{
            if (xhr.readyState == 4 && xhr.status == 200){                
                console.log("Request Sent")                
                window.location.href = xhr.responseURL;                           
            } else if (xhr.readyState == 2 && xhr.status == 404){
                alert("Wrong credentials!");
                location.reload();
            }
        }        
        xhr.send(JSON.stringify({"user": user, "password": pass, "t_offset": t_offset}));
    }
    else{
        alert("Fill the User and Password.")        
    }    
}

function register() {
    var regUser = document.querySelector("#user");
    var regPassword = document.querySelector("#password");
    var user = regUser.value;
    var pass = regPassword.value;
    if (user && pass){
        var xhr = new XMLHttpRequest();
        xhr.open('POST', "/register", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = ()=>{
            if (xhr.readyState == 4 && xhr.status == 200){                
                console.log("Request Sent")
                alert("User added Successfully")
                window.location.href = xhr.responseURL;                
            } else if (xhr.readyState == 4 && xhr.status == 409){
                alert("User already exists");
                location.reload();
            }
        }        
        xhr.send(JSON.stringify({"user": user, "password": pass}));                
    }
    else{
        alert("Fill the User and Password.")        
    }    
}