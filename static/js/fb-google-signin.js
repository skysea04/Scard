// FB login
const fbBtn = document.querySelector('.fb-btn')
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
                email : `FB_${user.email}`,
                password : user.id,
                fromAPI: true
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

// Google Signin
function handleClientLoad() {
    // Load the API's client and auth2 modules.
    // Call the initClient function after the modules load.
    gapi.load('client:auth2', initClient);
}
function initClient() {
    gapi.client.init({
        'clientId': '46769118537-mq0m5m2589ea8euptnha9903r2a85l18.apps.googleusercontent.com',
        'cookiepolicy': "single_host_origin",
        'scope': SCOPE
    }).then(function () {
        GoogleAuth = gapi.auth2.getAuthInstance();
        
        // Listen for sign-in state changes.
        GoogleAuth.isSignedIn.listen(updateSigninStatus);
        
        // Handle initial sign-in state. (Determine if user is already signed in.)
        // var user = GoogleAuth.currentUser.get();
        // setSigninStatus();
        
        googleBtn.addEventListener('click', ()=>{
            GoogleAuth.signIn()
            setSigninStatus()
        })
    });
}
const googleBtn = document.querySelector('.google-signin')


function setSigninStatus() {
    var user = GoogleAuth.currentUser.get();
    var isAuthorized = user.hasGrantedScopes(SCOPE);
    if (isAuthorized) {
        console.log(user.dt.Nt, user.dt.LS)
        const signupData = {
            email : `GOOGLE_${user.dt.Nt}`,
            password : user.dt.LS,
            fromAPI: true 
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

    } else {
        console.log('not login')
    }
}
function updateSigninStatus() {
    setSigninStatus();
}
