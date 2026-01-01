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