$(document).ready(function(){
    $("#loginForm").submit(function(e){
        e.preventDefault();
        var password = $("#password").val();
        if(password !== "123456"){
            alert("Incorrect password! Please try again.");
        } else {
			window.location.href="MAP.html";
            alert("Login successful!");
        }
    });
});