//網址ID
const postID = location.pathname.split('/').pop()
// API
const postAPI = `/api/post/${postID}`
const commentAPI = `/api/comment/${postID}`
const postLikeAPI = `/api/post/${postID}/like`
const postFollowAPI = `/api/post/${postID}/follow`
const newPostAPI = '/api/new-post'
const postImageAPI = '/api/new-post/image'

//// 匯入文章至頁面
const thePost = document.querySelector('.the-post')
const postAvatar = thePost.querySelector('.author-field img')
const postUserName = thePost.querySelector('.author-field .user-name')
const postTitle = thePost.querySelector('.post-title')
const postBoard = thePost.querySelector('.post-board')
const postCreateTime = thePost.querySelector('.create-time')
const postContent = thePost.querySelector('.post-content')
const postLikeCount = thePost.querySelector('.like-count')
const postLikeIcon = thePost.querySelector('.like')
const postFollowIcon = thePost.querySelector('.follow')
const postCommentCounts = document.querySelectorAll('.comment-count')

const comments = document.querySelector('.comments')
const cmtLst = comments.querySelector('#comment-list')

let showCmt = true
// 獲得文章內容
fetch(postAPI)
.then(res => res.json())
.then(data => {
    postAvatar.src = data.avatar
    postUserName.innerText = data.userName
    postTitle.innerText = data.title
    postBoard.href = data.boardSrc
    postBoard.innerText = data.boardName
    postCreateTime.innerText = data.createTime
    let cleanContent = DOMPurify.sanitize( data.content , {USE_PROFILES: {html: true}} );
    postContent.innerHTML = cleanContent
    postLikeCount.innerText = data.likeCount
    postCommentCounts.forEach( count =>{
        count.innerText = data.commentCount
    })
    if(data.like){
        postLikeIcon.classList.add('active')
    }
    if(data.follow){
        postFollowIcon.classList.add('active')
    }
    if(data.isAuthor){
        postFollowIcon.classList.add('d-none')
        //// 建立編輯、刪除文章的元件與函式
        // delModal變數
        const delModalContain = document.getElementById('del-modal')
        const delModal = new bootstrap.Modal(delModalContain)
        const delModalBody = delModalContain.querySelector('.modal-body')
        const delModalHref = delModalContain.querySelector('.modal-href')
        
        // 編輯文章元件
        const editHref = document.createElement('a')
        editHref.className = 'scard-l btn rounded-0'
        editHref.innerText = '編輯文章'
        editHref.href = `${location.pathname}/edit`
        
        // 刪除文章元件
        const delHref = document.createElement('a')
        delHref.className = 'text-danger btn rounded-0'
        delHref.innerText = '刪除文章'

        async function delPost(){
            const res = await fetch(postAPI, {method: 'DELETE'})
            const data = await res.json()
            if(data.error){
                showErrorModal(data)
            }else{ // 成功刪除返回首頁
                location = '/b'
            }
        }
        
        // 請使用者確認是否刪除文章
        function showDelModal(){
            delModalHref.addEventListener('click', delPost)
            delModalBody.innerText = `確定要刪除本篇文章嗎？此操作無法復原。`
            delModal.show()
        }
        // 當modal被關閉時，取消delModalHref與刪除文章的事件關聯
        delModalContain.addEventListener('hidden.bs.modal', ()=>{
            delModalHref.removeEventListener('click', delPost)
        })
        
        delHref.addEventListener('click', showDelModal)
        
        // 包覆編輯＆刪除選項
        const editLst = document.createElement('div')
        editLst.className = 'd-flex flex-column'
        editLst.append(editHref, delHref)
        
        // 操作文章按鈕
        const editBtn = thePost.querySelector('.post-edit')
        editBtn.classList.remove('d-none')
        
        // 文章popover
        const editPopover = new bootstrap.Popover(editBtn, {
            container: 'body',
            placement: "bottom",
            html: true,
            trigger: 'manual',
            content: editLst
        })

        editBtn.addEventListener('click', ()=>{
            editPopover.toggle()
        })
        editBtn.addEventListener('blur', ()=>{
            editPopover.hide()
        })

    }

    // 如果留言數為0，顯示沒有留言的頁面配置
    if(data.commentCount == 0){
        comments.classList.add('d-none')
        showCmt = false
    }else{
        // 匯入留言至頁面
        fetch(commentAPI)
        .then(res => res.json())
        .then(data => {
            data.forEach(comment => {
                getComment(comment)
            })
        })
    }
})

// 匯入單筆留言
function getComment(comment){
    const floor = document.createElement('p')
    floor.className = 'floor'
    floor.innerText = `B${comment.floor}`

    const dot = document.createElement('p')
    dot.innerText = '・'
    
    const createTime = document.createElement('p')
    createTime.className = 'create-time'
    createTime.innerText = comment.createTime

    const cmtInfo = document.createElement('div')
    cmtInfo.className = 'd-flex'
    cmtInfo.append(floor, dot, createTime)
    
    // 使用者名稱
    const userName = document.createElement('p')
    userName.className = 'mb-0 user-name'
    userName.innerText = comment.userName

    const cmtAuthor = document.createElement('div')
    cmtAuthor.className = 'cmt-author'
    cmtAuthor.append(userName, cmtInfo)

    // 使用者頭像
    const avatar = document.createElement('img')
    avatar.className = 'me-2 rounded-circle avatar'
    avatar.src = comment.avatar

    const authorField = document.createElement('div')
    authorField.className = 'd-flex author-field'
    authorField.append(avatar, cmtAuthor)

    // 留言header
    const cmtHeader = document.createElement('div')
    cmtHeader.className = 'd-flex justify-content-between align-items-center text-black-50 fs-6 mb-3 comment-header'
    cmtHeader.append(authorField)
    
    // 如果留言存在，顯示按讚/編輯icon
    if(!comment.delete){
        const likeIcon = document.createElement('div')
        likeIcon.className = 'me-2'
        likeIcon.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-heart-fill" viewBox="0 0 16 15">
            <path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
        </svg>
        `
        const likeCount = document.createElement('p')
        likeCount.className = 'me-2'
        likeCount.innerText = comment.likeCount
        
        const likeField = document.createElement('div')
        likeField.className = 'd-flex align-items-center like'
        comment.like && likeField.classList.add('active')
        likeField.append(likeIcon, likeCount)
        

        const infoField = document.createElement('div')
        infoField.className = 'd-flex info-field post-interact'
        infoField.append(likeField)

        // 如果瀏覽者就是留言作者
        if(comment.isAuthor){
            
            // 分隔bar
            const infoBar = document.createElement('div')
            infoBar.className = 'info-bar my-auto bg-secondary mx-2'
            
            // 改動留言按鈕
            const editBtn = document.createElement('button')
            editBtn.className = 'edit btn p-0 text-secondary ms-1'
            editBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-pencil-fill" viewBox="0 0 16 16">
                <path d="M12.854.146a.5.5 0 0 0-.707 0L10.5 1.793 14.207 5.5l1.647-1.646a.5.5 0 0 0 0-.708l-3-3zm.646 6.061L9.793 2.5 3.293 9H3.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.207l6.5-6.5zm-7.468 7.468A.5.5 0 0 1 6 13.5V13h-.5a.5.5 0 0 1-.5-.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.5-.5V10h-.5a.499.499 0 0 1-.175-.032l-.179.178a.5.5 0 0 0-.11.168l-2 5a.5.5 0 0 0 .65.65l5-2a.5.5 0 0 0 .168-.11l.178-.178z"/>
            </svg>
            `
            // delModal變數
            const delModalContain = document.getElementById('del-modal')
            const delModal = new bootstrap.Modal(delModalContain)
            const delModalBody = delModalContain.querySelector('.modal-body')
            const delModalHref = delModalContain.querySelector('.modal-href')
            
            
            // 編輯文章元件
            const editHref = document.createElement('a')
            editHref.className = 'scard-l btn rounded-0'
            editHref.innerText = '編輯留言'
            
            // 刪除文章元件
            const delHref = document.createElement('a')
            delHref.className = 'text-danger btn rounded-0'
            delHref.innerText = '刪除留言'
            // delHref.addEventListener('click', showDelModal)
            
            // 包覆編輯＆刪除選項
            const editLst = document.createElement('div')
            editLst.className = 'd-flex flex-column'
            editLst.append(editHref, delHref)
            
            //api
            const theCommentAPI = `/api/comment/${comment.id}`

            // 編輯留言
            async function patchComment(){
                const commentData = {
                    content: postCommentContent.innerHTML
                }
                const res = await fetch(theCommentAPI, {
                    method: 'PATCH',
                    body: JSON.stringify(commentData),
                    headers: {'Content-Type': 'application/json'}
                })
                const data = await res.json()
                if(data.error){
                    showErrorModal(data)
                }else{
                    // 更新留言內容
                    cmtBody.innerHTML = comment.content = postCommentContent.innerHTML
                    closePatchComment()
                }
            }
            // 顯現留言面板
            function openPatchComment(){
                sendBtn.addEventListener('click', patchComment)
                postCommentContent.innerHTML = comment.content
                commentBlank.classList.add('d-none')
                postComment.classList.remove('d-none')
            }

            // 關閉留言面板
            function closePatchComment(){
                sendBtn.removeEventListener('click', patchComment)
                postCommentContent.innerHTML = '<p></b></p>'
                commentBlank.classList.remove('d-none')
                postComment.classList.add('d-none')
            }

            editHref.addEventListener('click', openPatchComment)
            cancelComment.addEventListener('click', closePatchComment)

            // 刪除留言
            async function delComment(){
                const res = await fetch(theCommentAPI, {method:'DELETE'})
                const data = await res.json()
                if(data.error){
                    showErrorModal(data)
                }else{
                    // 修正該留言內容為刪除版本樣式
                    avatar.src = '/static/icons/avatar/nobody.svg'
                    userName.innerText = '這則留言已被刪除'
                    cmtBody.innerHTML = '<p>已經刪除的內容就像Scard一樣，錯過是無法再相見的！</p>'
                    infoField.classList.add('d-none')
                    // delModal關閉
                    delModal.hide()
                }
            }

            // 請使用者確認是否刪除留言
            function showDelModal(){
                delModalHref.addEventListener('click', delComment)
                delModalBody.innerText = `確定要刪除本則留言嗎？此操作無法復原。`
                delModal.show()
            }
            // 當modal被關閉時，取消delModalHref與刪除文章的事件關聯
            delModalContain.addEventListener('hidden.bs.modal', ()=>{
                delModalHref.removeEventListener('click', delComment)
            })

            delHref.addEventListener('click', showDelModal)
            
            // 文章popover
            const editPopover = new bootstrap.Popover(editBtn, {
                container: 'body',
                placement: "bottom",
                html: true,
                trigger: 'manual',
                content: editLst
            })
            editBtn.addEventListener('click', ()=>{
                editPopover.toggle()
            })
            editBtn.addEventListener('blur', ()=>{
                editPopover.hide()
            })

            infoField.append(infoBar, editBtn)
        }
        cmtHeader.append(infoField)
        //按讚API
        const cmtLikeAPI = `/api/comment/${comment.id}/like`
        async function cmtClickLike(){
            const res = await fetch(cmtLikeAPI, {method: "PATCH"})
            const data = await res.json()
            if(data.error){
                showErrorModal(data)
            }
            else{
                likeCount.innerText = data.likeCount
                likeField.classList.toggle('active')
            }
        }
        likeField.addEventListener('click', cmtClickLike)
    }
    
    // 留言body
    const cmtBody = document.createElement('div')
    cmtBody.className = 'comment-body'
    cmtBody.innerHTML = comment.content
    
    // 把留言全部包起來
    const cmt = document.createElement('li')
    cmt.className = 'list-group-item px-0 py-3 comment'
    cmt.append(cmtHeader, cmtBody)
    
    // 加入留言列表
    cmtLst.append(cmt)
}

// 對文章按讚
async function clickLike(){
    const res = await fetch(postLikeAPI, {method: 'PATCH'})
    const data = await res.json()
    if(data.error){
        showErrorModal(data)
    }
    else{
        postLikeCount.innerText = data.likeCount
        postLikeIcon.classList.toggle('active')
    }
}
postLikeIcon.addEventListener('click', clickLike)
// 追蹤文章
async function clickFollow(){
    const res = await fetch(postFollowAPI, {method: 'PATCH'})
    const data = await res.json()
    if(data.error){
        showErrorModal(data)
    }
    else{
        postFollowIcon.classList.toggle('active')
        if(data.isFollow){ //使用者追蹤貼文，幫使用者加入頻道
            socket.emit('sub_channel', `post_${postID}`)
        }else{
            socket.emit('unsub_channel', `post_${postID}`)
        }
    }
}
postFollowIcon.addEventListener('click', clickFollow)


//// 使用者留言撰寫區
const commentBlank = document.querySelector('.comment-blank')
const postComment = document.querySelector('.post-comment') // 留言撰寫區塊
const cancelComment = postComment.querySelector('.cancel')
const postCommentContent = postComment.querySelector('.post-comment-content') //留言內容區塊
const postCommentAvatar = postComment.querySelector('.post-comment-avatar')
const nameSelect = postComment.querySelector('.name-select')
const sendBtn = postComment.querySelector('.send-comment')
const expandBtn = postComment.querySelector('#expand-btn')
const contractBtn = postComment.querySelector('#contract-btn')

// 將個人名稱資訊匯入留言區
fetch(newPostAPI)
    .then(res => res.json())
    .then(data => {
        if(data.error){ 
            //點擊時出現錯誤，顯示提示Modal
            commentBlank.addEventListener('click',()=>{
                showErrorModal(data)
            })
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
            postCommentAvatar.src = data.avatar

            commentBlank.addEventListener('click', openPostComment)
            cancelComment.addEventListener('click', closePostComment)
        }
    })

// 顯現留言面板
function openPostComment(){
    sendBtn.addEventListener('click', sendComment)
    commentBlank.classList.add('d-none')
    postComment.classList.remove('d-none')
}

// 關閉留言面板
function closePostComment(){
    sendBtn.removeEventListener('click', sendComment)
    commentBlank.classList.remove('d-none')
    postComment.classList.add('d-none')
}

// 擴展/縮小留言面板區域
function commentExpandToggle(){
    postComment.classList.toggle('expand')
    expandBtn.classList.toggle('d-none')
    contractBtn.classList.toggle('d-none')
}
expandBtn.addEventListener('click', commentExpandToggle)
contractBtn.addEventListener('click', commentExpandToggle)

// 編輯留言的相關變數
let postCommentContentHTML = postCommentContent.innerHTML
let allContent = postCommentContent.childNodes
let textCursor = allContent[allContent.length - 2]

// 每次輸入內文就會儲存完整html
function inputSave(){
    selectImages()
    postCommentContentHTML = postCommentContent.innerHTML
    if(postCommentContentHTML == ''){
        postCommentContent.innerHTML = '<p><br></p>'
        textCursor = postCommentContent.querySelector('p')
    }else{
        textCursor = window.getSelection().anchorNode
        if(textCursor.nodeName == '#text'){
            textCursor = textCursor.parentNode
        }
    }
}
// 在postCommentContent內更改點擊位置可以改變textCursor元素
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
                // textCursor = e.target.parentNode
                const words = s.split(/\n|\r/)
                const len = words.length
                for(let index = 0; index < len; index++){
                    // console.log(words[index])
                    if(words[index] == '') continue
                    const page = document.createElement('p')
                    page.innerText = words[index]
                    textCursor.insertAdjacentElement('afterend', page)
                    textCursor = page
                }
            });
        } else if ((pasteData[i].kind == 'string') &&
                    (pasteData[i].type.match('^text/html'))) {
            // Drag pasteData item is HTML
            console.log(e.target)
            // console.log("... Drop: HTML");
        } else if ((pasteData[i].kind == 'string') &&
                    (pasteData[i].type.match('^text/uri-list'))) {
            // Drag pasteData item is URI
            // console.log("... Drop: URI");
        } else if ((pasteData[i].kind == 'file') &&
                    (pasteData[i].type.match('^image/'))) {
            var f = pasteData[i].getAsFile();
            // 上傳圖片返回內容
            showUpload(f)
        }
    }
}
// 每次點擊皆改動
postCommentContent.addEventListener('click', changetextCursor)
// 每次輸入皆改動
postCommentContent.addEventListener('input', inputSave)
// 每次paste情況上傳照片或呈線文字
postCommentContent.addEventListener('paste', pasteSave)

// 上傳圖片到回覆內容中
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

// 發送留言
async function sendComment(){
    const commentData = {
        name: nameSelect.value,
        content: postCommentContent.innerHTML
    }
    const res = await fetch(commentAPI, {
        method: 'POST',
        body: JSON.stringify(commentData),
        headers: {'Content-Type': 'application/json'}
    })
    const data = await res.json()
    if(data.error){
        showErrorModal(data)
    }
    else{
        postCommentContent.innerHTML = '<p></b></p>'
        // 關閉留言編輯區
        closePostComment()

        // 加入留言到頁面
        getComment(data)

        // 更改留言數量
        postCommentCounts.forEach( cmtCount => {
            cmtCount.innerText = data.floor
        })

        if(!showCmt){ // 過去沒有留言，秀出留言區
            showCmt = true
            comments.classList.remove('d-none')
        }
        // 如果使用者還沒有追蹤該貼文，幫使用者自動追蹤
        if(data.addFollow){
            postFollowIcon.classList.add('active')
            socket.emit('follow_post', postID)
        }
    }

}
