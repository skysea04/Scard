//// errorModal相關變數
// const errorModalContain = document.getElementById('error-modal')
// const errorModal = new bootstrap.Modal(errorModalContain)
// const modalTitle = errorModalContain.querySelector('.modal-title')
// const modalBody = errorModalContain.querySelector('.modal-body')
// const modalHref = errorModalContain.querySelector('.modal-href')

modalHref.addEventListener('click',()=> errorModal.hide())

//// api資訊
const newPostAPI = '/api/new-post'
const postImageAPI = '/api/new-post/image'

//// 定義文章各欄位變數
const boardSelect = document.querySelector('.board-select')
const nameSelect = document.querySelector('.name-select')
const postTitle = document.querySelector('.post-title')
const postContent = document.querySelector('.post-content')
const postAvatar = document.querySelector('.post-avatar')
//// 將看版資訊與個人名稱資訊匯入
fetch(newPostAPI)
    .then(res => res.json())
    .then(data => {
        if(data.error){ //出現錯誤，顯示提示Modal
            showErrorModal(data)
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

            // 新增發文頭像
            postAvatar.src = data.avatar

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
if(!localStorage.getItem('newPostContent')){
    localStorage.setItem('newPostContent', '<p><br></p>')
}
postContent.innerHTML = localStorage.getItem('newPostContent')
let postContentHTML = postContent.innerHTML
let allContent = postContent.childNodes
let textCursor = allContent[allContent.length - 1]

// 每次輸入內文就會儲存完整html到localhost
function inputSave(){
    selectImages()
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
    }else if(tempCursor.nodeName == 'P'){
        textCursor = window.getSelection().anchorNode
    }
}
// 滿足貼上內容的情境，將文字與單一貼上的圖片留下
function pasteSave(e){
    e.preventDefault()
    const cp = e.clipboardData
    const pasteData = cp.items
    for (var i = 0; i < pasteData.length; i += 1) {
        if ((pasteData[i].kind == 'string') && 
            (pasteData[i].type.match('^text/plain'))) {
            // This item is the target node
            pasteData[i].getAsString(function (s){
                // console.log(s)
                // console.log(e.target)
                const words = s.split(/\n/)
                const len = words.length
                for(let index = 0; index < len; index++){
                    // console.log(words[index])
                    if(words[index] == '') continue
                    const page = document.createElement('p')
                    page.innerText = words[index]
                    textCursor.insertAdjacentElement('afterend', page)
                    textCursor = page
                }
                localStorage.setItem('newPostContent', postContent.innerHTML)
            });
        } else if ((pasteData[i].kind == 'string') &&
                    (pasteData[i].type.match('^text/html'))) {
            // Drag pasteData item is HTML
            console.log("... Drop: HTML");
        } else if ((pasteData[i].kind == 'string') &&
                    (pasteData[i].type.match('^text/uri-list'))) {
            // Drag pasteData item is URI
            console.log("... Drop: URI");
        } else if ((pasteData[i].kind == 'file') &&
                    (pasteData[i].type.match('^image/'))) {
            var f = pasteData[i].getAsFile();
            // 上傳圖片返回內容
            showUpload(f)
        }
    }
}
// 每次點擊皆改動
postContent.addEventListener('click', changetextCursor)
// 每次輸入皆改動
postContent.addEventListener('input', inputSave)
// 每次paste是情況上傳照片或呈線文字
postContent.addEventListener('paste', pasteSave)

//// 上傳圖片到文章中
const imgInput = document.querySelector('#img')
const uploadImgSpinner = document.querySelector('.upload-img-spinner')
async function showUpload(inputImage){
    // 讀取圈圈轉起來
    uploadImgSpinner.classList.remove('d-none')
    
    const imgData = new FormData();
    console.log(imgData)
    imgData.append('image', inputImage) 
    console.log(imgInput)
    const res = await fetch(postImageAPI, {
        method: 'POST',
        body: imgData
    })
    const data = await res.json()
    
    // 得到結果，讀取圈圈消失
    uploadImgSpinner.classList.add('d-none')

    if(data.ok){
        const imgSelf = document.createElement('img')
        imgSelf.className = 'upload-img'
        imgSelf.src = data.src
        if(textCursor.innerHTML == '<br>'){
            textCursor.innerHTML = ''
            textCursor.append(imgSelf)
        }else{
            const imgContainer = document.createElement('p')
            imgContainer.appendChild(imgSelf)
            textCursor.insertAdjacentElement('afterend', imgContainer)
            textCursor = imgContainer
        }
        
        // 儲存到localStorage
        postContentHTML = postContent.innerHTML
        localStorage.setItem('newPostContent', postContentHTML);
        selectImages()   
    }else{
        showErrorModal(data)
    }    
}
imgInput.addEventListener('change',()=>{
    showUpload(imgInput.files[0])
})

// 點選上傳圖片時，可以選取整張圖
function selectImages(){
    let contentImgs = document.querySelectorAll('p .upload-img')
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
        showErrorModal(data)
    }else{
        localStorage.setItem('newPostTitle', '')
        localStorage.setItem('newPostContent', '<p><br></p>')
        window.location = data.url
    }
}

sendPostBtn.addEventListener('click', sendPost)