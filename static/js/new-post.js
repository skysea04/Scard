//// errorModal相關變數
const errorModalContain = document.getElementById('error-modal')
const errorModal = new bootstrap.Modal(errorModalContain)
const modalTitle = errorModalContain.querySelector('.modal-title')
const modalBody = errorModalContain.querySelector('.modal-body')
const modalHref = errorModalContain.querySelector('.modal-href')

modalHref.addEventListener('click',()=> errorModal.hide())

//// api資訊
const newPostAPI = '/api/new-post'
const postImageAPI = '/api/new-post/image'

//// 定義文章各欄位變數
const boardSelect = document.querySelector('.board-select')
const nameSelect = document.querySelector('.name-select')
const postTitle = document.querySelector('.post-title')
const postContent = document.querySelector('.post-content')

//// 將看版資訊與個人名稱資訊匯入
fetch(newPostAPI)
    .then(res => res.json())
    .then(data => {
        if(data.error){ //出現錯誤，顯示提示Modal
            modalTitle.innText = data.title
            modalBody.innerText = data.message
            modalHref.innerText = data.confirm
            modalHref.href = data.url
            errorModal.show()
        }
        else{
            // 新增發文身份名稱選項
            const fullName = document.createElement('option')
            fullName.value = 'full'
            fullName.innerText = `${data.collage} ${data.department}`
            const collageName = document.createElement('option')
            collageName.value = 'collage'
            collageName.innerText = data.collage
            const anonymous = document.createElement('option')
            anonymous.value = '匿名'
            anonymous.innerText = '匿名'
            nameSelect.append(fullName, collageName, anonymous)

            // 新增發文看板選項
            data.boardList.forEach(board => {
                const boardOption = document.createElement('option')
                boardOption.value = board.boardId
                boardOption.innerText = board.showName
                boardSelect.append(boardOption)
            })
        }
    })

//// 儲存文章標題
postTitle.value = localStorage.getItem('newPostTitle')
function savePostTitle(){
    localStorage.setItem('newPostTitle', postTitle.value)
}
postTitle.addEventListener('input', savePostTitle)

//// 內文編輯器
postContent.innerHTML = localStorage.getItem('newPostContent')
let postContentHTML = postContent.innerHTML
let allContent = postContent.childNodes
let textCursor = allContent[allContent.length - 1]

// 每次輸入內文就會儲存完整html到localhost
function inputSave(){
    postContentHTML = postContent.innerHTML
    if(postContentHTML == ''){
        postContentHTML = '<p><br></p>'
        localStorage.setItem('newPostContent', postContentHTML)
        postContent.innerHTML = localStorage.getItem('newPostContent')
        textCursor = postContent.querySelector('p')
    }else{
        textCursor = window.getSelection().anchorNode
        if(textCursor.nodeName == '#text'){
            textCursor = textCursor.parentNode
        }
        localStorage.setItem('newPostContent', postContentHTML)
    }
}
// 在postContent內更改點擊位置可以改變textCursor元素
function changetextCursor(){
    tempCursor = window.getSelection().anchorNode
    if(tempCursor.nodeName == '#text' && tempCursor.parentNode.nodeName=='P'){
        textCursor = window.getSelection().anchorNode.parentElement
    }else if(tempCursor.nodeName == 'p'){
        textCursor = window.getSelection().anchorNode
    }else if(tempCursor.firstChild && tempCursor.firstChild.classList){
        if(tempCursor.firstChild.classList.contains('upload-img')){
            textCursor = window.getSelection().anchorNode
        }
    }
}
// 每次點擊皆改動
postContent.addEventListener('input', inputSave)
document.addEventListener('selectionchange', changetextCursor)

// 點選上傳圖片時，可以整個選取
function selectImages(){
    let contentImgs = document.querySelectorAll('div .upload-img')
    contentImgs.forEach(contentImg => {
        function selectImg(){
            let selection = window.getSelection()
            selection.removeAllRanges()
            let theImage = this
            let range = document.createRange()
            range.selectNode(theImage)
            selection.addRange(range)
        }
        contentImg.addEventListener('click', selectImg)
    })
}
// 先執行一次
selectImages()

//// 上傳圖片到文章中
const imgInput = document.querySelector('#img')
async function showUpload(){
    const imgData = new FormData();
    imgData.append('image', imgInput.files[0]) 
    const res = await fetch(postImageAPI, {
        method: 'POST',
        body: imgData
    })
    const data = await res.json()
    if(data.ok){
        const imgContainer = document.createElement('div')
        const imgSelf = document.createElement('img')
        imgSelf.className = 'upload-img'
        imgSelf.src = data.src
        imgContainer.appendChild(imgSelf)
        textCursor.insertAdjacentElement('afterend', imgContainer)
        textCursor = imgContainer
        

        postContentHTML = postContent.innerHTML
        localStorage.setItem('newPostContent', postContentHTML);
        selectImages()   
    }else{
        modalTitle.innText = data.title
        modalBody.innerText = data.message
        modalHref.innerText = data.confirm
        modalHref.href = data.url
        errorModal.show()
    }    
}
imgInput.addEventListener('change', showUpload)

//// 上傳貼文
const sendPostBtn = document.querySelector('.send-post')
async function sendPost(){
    const postData = {
        board: boardSelect.value,
        name: nameSelect.value,
        title: postTitle.value,
        content: postContent.innerHTML
    }
    const res = await fetch(newPostAPI, {
        method: 'POST',
        body: JSON.stringify(postData),
        headers: {'Content-Type': 'application/json'}
    })
    const data = await res.json()
    if(data.error){//出現錯誤，顯示提示Modal
        modalTitle.innText = data.title
        modalBody.innerText = data.message
        modalHref.innerText = data.confirm
        modalHref.href = data.url
        errorModal.show()
    }else{
        localStorage.setItem('newPostTitle', '')
        localStorage.setItem('newPostContent', '<p><br></p>')
        window.location = data.url
    }
}

sendPostBtn.addEventListener('click', sendPost)