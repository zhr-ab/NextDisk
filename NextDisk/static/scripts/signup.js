function submitForm() {
    // 获取错误信息显示元素
    const errorElement = document.getElementById('error-message');
    errorElement.textContent = ''; // 清空之前的错误信息

    // 获取表单元素值
    const username = document.getElementById('username').value;
    const password = document.getElementById('password1').value;
    const confirmPassword = document.getElementById('password2').value;

    // 验证逻辑
    if (!username || !password || !confirmPassword) {
        errorElement.textContent = '请填写完整的用户名和密码！';
        return false; // 阻止表单提交
    }

    if (password !== confirmPassword) {
        errorElement.textContent = '密码和确认密码不一致！';
        return false; // 阻止表单提交
    }

    // 所有验证通过，提交表单
    document.getElementById('registerForm').submit();
    return true;
}

// 兼容 DOMContentLoaded 的文件选择与头像预览
document.addEventListener('DOMContentLoaded', function(){
    var fileInput = document.querySelector('.file-input');
    var fileName = document.querySelector('.file-name');
    var fileBtn = document.querySelector('.file-btn');
    var avatar = document.querySelector('.avatar-preview');

    if(fileBtn && fileInput){
        fileBtn.addEventListener('click', function(e){
            e.preventDefault();
            fileInput.click();
        });
    }
    if(fileInput){
        fileInput.addEventListener('change', function(){
            var f = this.files[0];
            if(fileName) fileName.textContent = f ? f.name : '未选择文件';
            if(f && f.type && f.type.indexOf('image') === 0 && avatar){
                var reader = new FileReader();
                reader.onload = function(e){ avatar.src = e.target.result; }
                reader.readAsDataURL(f);
            }
        });
    }
});