// API
collageAPI = '/api/profile/collage'

// 使可填寫日期永遠在18年以前
const birthdayInput = document.querySelector('#birthday')
let maxDate = new Date()
let dd = maxDate.getDate()
let mm = maxDate.getMonth() + 1 //1月是0!
let yyyy = maxDate.getFullYear() - 18
if(dd < 10){
        dd = '0' + dd
    } 
if(mm < 10){
    mm = '0' + mm
} 
maxDate = yyyy + '-' + mm + '-' + dd
birthdayInput.setAttribute('max', maxDate)


// 匯入學校/系所資訊
const collSelect = document.querySelector('#collage')
const dptSelect = document.querySelector('#department')

// 匯入學校資訊
fetch(collageAPI)
.then(res => res.json())
.then(data => {
    if(data.error){
        console.log('伺服器錯誤')
    }else{
        data.data.forEach(coll => {
            const collOption = document.createElement('option')
            collOption.value = coll.id
            collOption.innerText = coll.name
            collSelect.appendChild(collOption)
        })
    }
})

// 當使用者選擇學校時，列出系所資訊
async function showDepartment(){
    // console.log(this.value)
    // 重置系所選項
    dptSelect.innerHTML = `<option value='' selected>選擇系所</option>`
    const dptAPI = `/api/profile/${this.value}/department`
    const res = await fetch(dptAPI)
    const data = await res.json()
    if(data.error){
        if(data.url){ //顯示伺服器錯誤訊息
            showErrorModal(data)
        }
        dptSelect.setAttribute('disabled', true)
    }
    else{
        data.data.forEach(dpt => {
            const dptOption = document.createElement('option')
            dptOption.value = dpt.id
            dptOption.innerText = dpt.name
            dptSelect.appendChild(dptOption)
        })
        dptSelect.removeAttribute('disabled')
    }
}
collSelect.addEventListener('change', showDepartment)


// 送出basicprofile表單
const basicProfileForm = document.querySelector('form.basic-profile')

async function postProfile(e){
    e.preventDefault()
    const profileData = {
        name : this.querySelector('input[name="name"]').value,
        gender : this.querySelector('select[name="gender"]').value,
        birthday : this.querySelector('input[name="birthday"]').value,
        collage : this.querySelector('select[name="collage"]').value,
        department : this.querySelector('select[name="department"]').value
    }
    const res = await fetch(profileAPI, {
        method: 'POST',
        body: JSON.stringify(profileData),
        headers: {'Content-Type': 'application/json'}
    })
    const data = await res.json()
    if(data.ok){
        window.location.replace('/')
    }else{
        const message = document.querySelector('.message')
        message.innerText = data.message
    }
}

basicProfileForm.addEventListener('submit', postProfile)