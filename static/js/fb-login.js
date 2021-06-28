const fbBtn = document.querySelector('.fb-login-button')
fbBtn.addEventListener("click", function (e) {
    e.preventDefault()
    checkLoginState()
})
function checkLoginState() {  // Called when a person is finished with the Login Button.
    FB.getLoginStatus(function(response) {   // See the onlogin handler
        statusChangeCallback(response);
    });
}

function statusChangeCallback(response) {  // Called with the results from FB.getLoginStatus().
    // console.log('statusChangeCallback');
    console.log(response);   // The current login status of the person.
    if (response.status === 'connected') {
        // 照理來說這個情況不應該發生
        console.log('有連上 直接獲取FB資訊登入') 
        getFBUserData()
        // Logged into your webpage and Facebook.
    } else {    // Not logged into your webpage or we are unable to tell.
        console.log('沒有連上 連結FB獲取資訊登入')
        fbLogin() 
    }
}
function fbLogin(){
    FB.login(response => {
        getFBUserData()
    },{ scope: "public_profile,email" })
}

function getFBUserData(){
    FB.api("/me", "GET", { fields: "id,email" }, user => {
        if (user.error) {
            console.log('error')
        } 
        else {
            console.log(user.id, user.email)
            const signupData = {
                email : user.email,
                password : user.id
            }
            fetch(userAPI, {
                method: 'POST',
                body: JSON.stringify(signupData),
                headers: {'Content-Type': 'application/json'}
            })
            .then(res => res.json())
            .then(data => {
                if(data.ok){
                    window.location.replace('/')
                }
                else{
                    const message = this.querySelector('.message')
                    message.innerText = data.message
                }
            })
        }
    })
}
