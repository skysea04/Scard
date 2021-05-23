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

// 送出basicprofile表單
const basicProfileForm = document.querySelector('form.basic-profile')

async function postProfile(e){
    e.preventDefault()
    const profileData = {
        name : this.querySelector('input[name="name"]').value,
        gender : this.querySelector('select[name="gender"]').value,
        birthday : this.querySelector('input[name="birthday"]').value,
        collage : this.querySelector('input[name="collage"]').value,
        department : this.querySelector('input[name="department"]').value
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