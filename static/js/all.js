// errorModal相關變數
const errorModalContain = document.getElementById('error-modal')
const errorModal = new bootstrap.Modal(errorModalContain)
const modalTitle = errorModalContain.querySelector('.modal-title')
const modalBody = errorModalContain.querySelector('.modal-body')
const modalHref = errorModalContain.querySelector('.modal-href')
modalHref.addEventListener('click',()=> errorModal.hide())

function showErrorModal(data){
    modalTitle.innerText = data.title
    modalBody.innerText = data.message
    modalHref.innerText = data.confirm
    modalHref.href = data.url
    errorModal.show()
}

// api
const userAPI = '/api/user'
const profileAPI = '/api/profile'
const myFollowPostAPI = '/api/post/my-follow'
const noteAPI = '/api/notification'

// socket
const socket = io()

// 根據是否登入顯示不同的nav內容
const navUser = document.querySelector('.nav-user')
const navStranger = document.querySelector('.nav-stranger')

async function checkSign(){
    const res =await fetch(userAPI)
    const data = await res.json()
    if(data.id){
        navUser.classList.add('d-flex')
        navStranger.classList.add('d-none')
        notification()
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

// 通知功能大禮包
function notification(){
    socket.on('connect', function(){
        fetch(myFollowPostAPI)
        .then(res => res.json())
        .then(data => {
            if(data.posts){
                data.posts.forEach( post => {
                    socket.emit('follow_post', post)
                })
            }
        })
    })

    // 通知
    const noteContainer = document.createElement('div')
    noteContainer.className = 'note-container overflow-auto py-3'

    const noteLst = document.createElement('div')
    noteLst.className = 'note-lst'

    const noteHeader = document.createElement('h5')
    noteHeader.className = 'mb-3 ms-3'
    noteHeader.innerText = '通知'
    noteContainer.append(noteHeader, noteLst)
    
    // 匯入過去通知
    fetch(noteAPI)
    .then(res => res.json())
    .then(data => {
        if(data.data){
            data.data.forEach(note => {
                createNote(note)
            })
        }
    })
    
    // 當新通知來時直接更新
    socket.on('receive_post_note', data => {
        console.log(data)
        createNote(data)
    })
    
    function createNote(data){
        const oldNote = noteLst.querySelector(`a[href="${data.href}"]`)
        if(oldNote){ //如果之前就有相同文章的通知，直接更改資訊即可
            const noteTime = oldNote.querySelector('.note-time')
            noteTime.innerText = data.time
            noteLst.prepend(oldNote)
        }
        else{ //創造新的通知訊息
            const note = document.createElement('a')
            note.className = 'note py-2'
            note.href = data.href
    
            const noteContent = document.createElement('p')
            noteContent.className = 'note-content mx-3 pb-1 text-body'
            noteContent.innerHTML = data.msg
    
            const noteTime = document.createElement('p')
            noteTime.className = 'note-time mx-3'
            noteTime.innerText = data.time
            
            note.append(noteContent, noteTime)
            noteLst.prepend(note)
        }
    }

    const noteBtn = document.querySelector('#notification')
    const notePopover = new bootstrap.Popover(noteBtn, {
        container: 'body',
        placement: "bottom",
        html: true,
        trigger: 'manual',
        content: noteContainer,
        offset: [120, 7]
    })
    noteBtn.addEventListener('click', ()=>{
        notePopover.toggle()
    })
    noteBtn.addEventListener('blur', ()=>{
        notePopover.hide()
    })
}

// 登出機制
const signoutBtn = document.querySelector('.signout')

async function signout(){
    await fetch(userAPI, {method: 'DELETE'})
    const userURL = location.pathname.split('/')[1]
    const toSignUpList = ['new-post', 'scard', 'message', 'my']
    // google登出
    try{googleSignout()}catch{}
    // FB登出
    try{fbLogout()}catch{}

    if(toSignUpList.includes(userURL)){
        location = '/signup'
    }else{
        location.reload()
    }
    // checkSign()
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


// fb登出
function fbLogout() {
    FB.logout(res => {
        // Person is now logged out
        // console.log("logout!!!!");
    });
} 

// FaceBook SDK 初始化
window.fbAsyncInit = function() {
    FB.init({
        appId      : '164377919057019',
        cookie     : true,  
        xfbml      : true,
        version    : 'v11.0'
    });
    FB.AppEvents.logPageView();
};

(function(d, s, id){
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {return;}
    js = d.createElement(s); js.id = id;
    js.src = "https://connect.facebook.net/zh_TW/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));


// Google OAuth 初始化
var GoogleAuth;
var SCOPE = 'profile email';
function handleClientLoad() {
    // Load the API's client and auth2 modules.
    // Call the initClient function after the modules load.
    gapi.load('client:auth2', initClient);
}

function initClient() {
    // In practice, your app can retrieve one or more discovery documents.
    // var discoveryUrl = 'https://www.googleapis.com/discovery/v1/apis/drive/v3/rest';

    // Initialize the gapi.client object, which app uses to make API requests.
    // Get API key and client ID from API Console.
    // 'scope' field specifies space-delimited list of access scopes.
    gapi.client.init({
        'clientId': '46769118537-mq0m5m2589ea8euptnha9903r2a85l18.apps.googleusercontent.com',
        'cookiepolicy': "single_host_origin",
        'scope': SCOPE
    }).then(function () {
        GoogleAuth = gapi.auth2.getAuthInstance();

    });
}

function googleSignout(){
    if (GoogleAuth.isSignedIn.get()) {
        // User is authorized and has clicked "Sign out" button.
        GoogleAuth.signOut();
    } 
}

function setSigninStatus() {
    var user = GoogleAuth.currentUser.get();
    var isAuthorized = user.hasGrantedScopes(SCOPE);
    if (isAuthorized) {
        console.log('Signin')
        console.log(user.dt.Nt, user.dt.LS)
    } else {
        console.log('not signin')
    }
}