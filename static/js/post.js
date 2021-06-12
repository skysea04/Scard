const editField = document.querySelector('.post-content')
const imgInput = document.querySelector('#img')
function showUpload(){
    const [file] = imgInput.files
    if(file){
        const imgContainer = document.createElement('div')
        const imgSelf = document.createElement('img')
        imgSelf.className = 'upload-img'
        imgSelf.src = URL.createObjectURL(file)
        imgContainer.appendChild(imgSelf)
        editField.appendChild(imgContainer)
        function getFocus(){
            console.log('aaa')
            imgSelf.focus()
            console.log(imgSelf)
        }
        imgContainer.addEventListener('click', getFocus)
    }
}
imgInput.addEventListener('change', showUpload)