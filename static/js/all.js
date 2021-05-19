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
    }
}
// 啟動一次
checkSign()

// 登出機制
const signoutBtn = document.querySelector('.signout')

async function signout(){
    await fetch(userAPI, {method: 'DELETE'})
    checkSign()
}

signoutBtn.addEventListener('click', signout)