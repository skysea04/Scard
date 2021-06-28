// errorModal相關變數
const errorModalContain = document.getElementById('error-modal')
const errorModal = new bootstrap.Modal(errorModalContain)
const modalTitle = errorModalContain.querySelector('.modal-title')
const modalBody = errorModalContain.querySelector('.modal-body')
const modalHref = errorModalContain.querySelector('.modal-href')
modalHref.addEventListener('click',()=> errorModal.hide())


// api
const userAPI = '/api/user'
const profileAPI = '/api/profile'

// 根據是否登入顯示不同的nav內容
const navUser = document.querySelector('.nav-user')
const navStranger = document.querySelector('.nav-stranger')

async function checkSign(){
    const res =await fetch(userAPI)
    const data = await res.json()
    if(data.id){
        navUser.classList.add('d-flex')
        navStranger.classList.add('d-none')
    }
    else{
        navUser.classList.remove('d-flex')
        navStranger.classList.add('d-flex')
        navStranger.classList.remove('d-none')
        try{
            const toSignupModal = new bootstrap.Modal(document.getElementById('to-signup-modal'))
            toSignupModal.show()
        }catch{}
    }
}
// 啟動一次
checkSign()

// 登出機制
const signoutBtn = document.querySelector('.signout')

async function signout(){
    FB.getLoginStatus(function(response) {
        // 檢查登入狀態
        if (response.status === "connected") {
            // 移除授權
            FB.api("/me/permissions", "DELETE", function(res) {
            // 用戶登出
            FB.logout();
            });
        } else {
            // do something
        }
    });
    await fetch(userAPI, {method: 'DELETE'})
    const userURL = location.pathname.split('/')[1]
    const toSignUpList = ['new-post', 'scard', 'message', 'my']
    if(toSignUpList.includes(userURL)){
        location = '/signup'
    }else{
        location.reload()
    }
    checkSign()
}

signoutBtn.addEventListener('click', signout)


// 確認使用者的權限是否可以進入某個頁面
const links = navUser.querySelectorAll('a')

async function verifyUser(e){
    e.preventDefault()
    // console.log(this.id)
    const verifyAPI = `/api/verify?a=${this.id}`
    const res = await fetch(verifyAPI)
    const data = await res.json()
    if(data.ok){
        location.assign(data.url)
    }else{
        modalTitle.innText = data.title
        modalBody.innerText = data.message
        modalHref.innerText = data.confirm
        modalHref.href = data.url
        errorModal.show()
    }

}

links.forEach(link => {
    link.addEventListener('click', verifyUser)
})




function statusChangeCallback(response) {  // Called with the results from FB.getLoginStatus().
    console.log('statusChangeCallback');
    console.log(response);                   // The current login status of the person.
    if (response.status === 'connected') {
        // getFBUserData()
        console.log('有連上') 
        // Logged into your webpage and Facebook.
    } else {                                 // Not logged into your webpage or we are unable to tell.
        testAPI();  
        console.log('沒有連上 笑死')
        // document.getElementById('status').innerHTML = 'Please log ' +
    //     'into this webpage.';
    }
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

function checkLoginState() {               // Called when a person is finished with the Login Button.
    FB.getLoginStatus(function(response) {   // See the onlogin handler
        statusChangeCallback(response);
    });
}

function testAPI() {
// Testing Graph API after login.  See statusChangeCallback() for when this call is made.
// console.log("Welcome!  Fetching your information.... ");
    FB.login(response => {
        // console.log(response);
        FB.api("/me", "GET", { fields: "id,email" }, user => {
            if (user.error) {
                console.log('error')
            } 
            else {
                // pro.src = user.picture.data.url
                // window.localStorage["url"] = user.picture.data.url
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
                console.log(user.id, user.email)
            }
        });
    },{ scope: "public_profile,email" })
}

window.fbAsyncInit = function() {
    FB.init({
        appId      : '164377919057019',
        cookie     : true,  
        xfbml      : true,
        version    : 'v11.0'
    });
    FB.AppEvents.logPageView();
    FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
    });
};

(function(d, s, id){
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {return;}
    js = d.createElement(s); js.id = id;
    js.src = "https://connect.facebook.net/zh_TW/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));