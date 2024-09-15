var topicIdTextBox = document.getElementById("topic-id");
if (topicIdTextBox){
    topicIdTextBox.addEventListener("keypress", event=>{
        if (event.key == "Enter") doneTopic();
    })
}

var toggler = document.getElementsByClassName("caret");
for (let i=0; i< toggler.length; i++){    
    let item = toggler[i];
    item.addEventListener("click", function(){        
        this.parentElement.querySelector(".nested").classList.toggle("active");
        this.classList.toggle("caret-down");
    })
}

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
        xhr.open('POST', "/add-topics.html",true)
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = ()=>{
            if (xhr.readyState == 4 && xhr.status == 200){
                console.log("Added the Topic")
            }
        }

        var pad = '00'
        var today = new Date().toLocaleDateString("en-US");
        var mdy = today.split('/');
        var month = (pad+mdy[0]).slice(-2);
        var day = (pad+mdy[1]).slice(-2);
        var year = mdy[2];
        today = year + "-" + month + "-" + day;
        var json  = new Object();
        json["topics"] = new Object();        
        topics.forEach(t => {            
            json["topics"][t] = new Object();
            json["topics"][t]["subject"] = subject.toUpperCase();
            json["topics"][t]["todo"] = today;
            json["topics"][t]["timesDone"] = 0;
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

function doneTopic(action, topic) {    
    var xhr = new XMLHttpRequest();
    xhr.open('GET', "/"+action+"/"+topic, false)
    xhr.onreadystatechange = ()=>{
        if (xhr.readyState == 4 && xhr.status == 200){                
            console.log("Done Topic")
        }
    }
    xhr.send();   
    location.reload()
}