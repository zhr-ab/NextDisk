// Final_setting.js
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM loaded - initializing scripts');

    const form = document.getElementById('finalSettingsForm');
    const errorMessage = document.getElementById('errorMessage');
    const confirmBtn = document.getElementById('confirmBtn');
    const overlay = document.getElementById('overlay');

    // 显示错误信息函数
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';

        // 5秒后自动隐藏错误信息
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }

    // 隐藏错误信息函数
    function hideError() {
        errorMessage.style.display = 'none';
    }

    // 表单验证函数
    function validateForm() {
        hideError();

        // 检查应用选择（至少选择一个）
        const appCheckboxes = document.querySelectorAll('input[name="apps"]:checked');
        if (appCheckboxes.length === 0) {
            showError('请至少选择一个要安装的应用！');
            // 添加错误样式到复选框容器
            const fieldset = document.querySelector('fieldset');
            if (fieldset) {
                fieldset.classList.add('field-error');
            }
            return false;
        } else {
            // 移除错误样式
            const fieldset = document.querySelector('fieldset');
            if (fieldset) {
                fieldset.classList.remove('field-error');
            }
        }

        // 检查数据存储路径
        const dataPath = document.querySelector('input[name="datapath"]');
        if (!dataPath.value.trim()) {
            showError('请填写数据/配置文件储存位置！');
            dataPath.focus();
            dataPath.classList.add('field-error');
            return false;
        } else {
            dataPath.classList.remove('field-error');
        }

        // 检查数据库类型
        const dbType = document.querySelector('input[name="dbtype"]');
        if (!dbType.value) {
            showError('请选择数据库类型！');
            const customSelect = document.querySelector('.custom-select');
            if (customSelect) {
                customSelect.classList.add('field-error');
            }
            return false;
        } else {
            const customSelect = document.querySelector('.custom-select');
            if (customSelect) {
                customSelect.classList.remove('field-error');
            }
        }

        return true;
    }

    // 确认按钮点击事件 - 验证表单并显示窗口
    if (confirmBtn && overlay) {
        confirmBtn.addEventListener('click', function (e) {
            e.preventDefault();
            console.log('Confirm button clicked - validating form');

            // 验证表单
            if (validateForm()) {
                console.log('Form validation passed - showing overlay');
                overlay.classList.add('show');
                document.body.classList.add('overlay-open');
            } else {
                console.log('Form validation failed');
            }
        });
    }

    // 窗口确定按钮 - 提交表单
    const winOk = document.getElementById('winOk');
    if (winOk) {
        winOk.addEventListener('click', function (e) {
            e.preventDefault();
            console.log('OK button clicked - submitting form');

            // 显示加载状态
            winOk.disabled = true;
            winOk.textContent = '提交中...';
            winOk.style.opacity = '0.7';

            // 再次验证表单（确保数据仍然有效）
            if (validateForm()) {
                console.log('Final validation passed - submitting to backend');

                // 收集所有数据
                const formData = new FormData();

                // 添加应用选择
                const appCheckboxes = document.querySelectorAll('input[name="apps"]:checked');
                appCheckboxes.forEach((checkbox, index) => {
                    formData.append(`apps[${index}]`, checkbox.value);
                });

                // 添加其他表单数据
                const dataPath = document.querySelector('input[name="datapath"]').value;
                const autostart = document.querySelector('input[name="autostart"]').checked;
                const dbType = document.querySelector('input[name="dbtype"]').value;

                formData.append('datapath', dataPath);
                formData.append('autostart', autostart);
                formData.append('dbtype', dbType);

                console.log('Form data:', {
                    apps: Array.from(appCheckboxes).map(cb => cb.value),
                    datapath: dataPath,
                    autostart: autostart,
                    dbtype: dbType
                });

                // 提交表单到后端
                fetch('/submit', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                    .then(response => {
                        console.log('Response status:', response.status);
                        console.log('Response ok:', response.ok);

                        if (response.ok) {
                            return response.json().catch(() => {
                                // 如果响应不是JSON，但仍然成功
                                return { success: true };
                            });
                        } else {
                            return response.json().then(errorData => {
                                throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
                            }).catch(() => {
                                throw new Error(`HTTP error! status: ${response.status}`);
                            });
                        }
                    })
                    .then(data => {
                        console.log('Form submitted successfully:', data);

                        // 显示成功消息
                        showNotification('设置提交成功！正在跳转...', 'success');

                        // 延迟跳转以便用户看到成功消息
                        setTimeout(() => {
                            console.log('Redirecting to /home');
                            window.location.href = '/home';
                        }, 1500);

                    })
                    .catch(error => {
                        console.error('Form submission error:', error);

                        // 恢复按钮状态
                        winOk.disabled = false;
                        winOk.textContent = '确定';
                        winOk.style.opacity = '1';

                        showError('提交失败: ' + error.message);

                        // 关闭窗口
                        closeWindow();
                    });
            } else {
                // 恢复按钮状态
                winOk.disabled = false;
                winOk.textContent = '确定';
                winOk.style.opacity = '1';
            }
        });
    }

    // 窗口关闭功能
    const winClose = document.getElementById('winClose');
    const winCancel = document.getElementById('winCancel');

    function closeWindow() {
        console.log('Closing window');
        if (overlay) {
            overlay.classList.remove('show');
            document.body.classList.remove('overlay-open');
        }

        // 恢复确定按钮状态
        const winOk = document.getElementById('winOk');
        if (winOk) {
            winOk.disabled = false;
            winOk.textContent = '确定';
            winOk.style.opacity = '1';
        }
    }

    if (winClose) {
        winClose.addEventListener('click', function (e) {
            e.preventDefault();
            closeWindow();
        });
    }

    if (winCancel) {
        winCancel.addEventListener('click', function (e) {
            e.preventDefault();
            closeWindow();
        });
    }

    // 点击 overlay 背景关闭窗口
    if (overlay) {
        overlay.addEventListener('click', function (e) {
            if (e.target === overlay) {
                closeWindow();
            }
        });
    }

    // ESC键关闭窗口
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && overlay && overlay.classList.contains('show')) {
            closeWindow();
        }
    });

    // 实时验证输入字段
    const dataPathInput = document.querySelector('input[name="datapath"]');
    if (dataPathInput) {
        dataPathInput.addEventListener('input', function () {
            if (this.value.trim()) {
                this.classList.remove('field-error');
            }
        });
    }

    // 实时验证应用选择
    const appCheckboxes = document.querySelectorAll('input[name="apps"]');
    appCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const selectedApps = document.querySelectorAll('input[name="apps"]:checked');
            if (selectedApps.length > 0) {
                // 移除所有复选框的错误样式
                const fieldset = document.querySelector('fieldset');
                if (fieldset) {
                    fieldset.classList.remove('field-error');
                }
            }
        });
    });

    // 自定义下拉组件功能
    const customSelects = document.querySelectorAll('.custom-select');
    customSelects.forEach(select => {
        const selected = select.querySelector('.select-selected');
        const options = select.querySelector('.select-items');
        const hiddenInput = select.querySelector('input[type="hidden"]');
        const optionsList = select.querySelectorAll('.select-option');

        if (selected && options) {
            selected.addEventListener('click', function (e) {
                e.stopPropagation();
                closeAllSelects();
                options.classList.toggle('show');
                selected.classList.toggle('active');

                // 移除错误样式
                select.classList.remove('field-error');
            });

            optionsList.forEach(option => {
                option.addEventListener('click', function () {
                    const value = this.getAttribute('data-value');
                    const text = this.querySelector('.option-text').textContent;

                    selected.querySelector('.selected-text').textContent = text;
                    if (hiddenInput) hiddenInput.value = value;

                    optionsList.forEach(opt => opt.classList.remove('selected'));
                    this.classList.add('selected');

                    options.classList.remove('show');
                    selected.classList.remove('active');

                    // 移除错误样式
                    select.classList.remove('field-error');
                });
            });
        }
    });

    function closeAllSelects() {
        document.querySelectorAll('.select-items').forEach(item => {
            item.classList.remove('show');
        });
        document.querySelectorAll('.select-selected').forEach(selected => {
            selected.classList.remove('active');
        });
    }

    // 复制密钥功能
    const readonlyInput = document.getElementById('readonlyInput');
    console.log('Readonly input:', readonlyInput);

    if (readonlyInput) {
        // 添加复制按钮
        const copyButton = document.createElement('button');
        copyButton.textContent = '复制密钥';
        copyButton.type = 'button';
        copyButton.className = 'copy-btn';
        copyButton.style.cssText = `
            margin-left: 10px;
            padding: 6px 12px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: background-color 0.3s ease;
        `;

        copyButton.addEventListener('mouseenter', function () {
            this.style.backgroundColor = '#218838';
        });

        copyButton.addEventListener('mouseleave', function () {
            this.style.backgroundColor = '#28a745';
        });

        copyButton.addEventListener('click', function (e) {
            e.preventDefault();
            copyToClipboard(readonlyInput.value);
        });

        // 将复制按钮插入到输入框后面
        readonlyInput.parentNode.insertBefore(copyButton, readonlyInput.nextSibling);

        // 打印功能
        const printButton = document.createElement('button');
        printButton.textContent = '打印密钥';
        printButton.type = 'button';
        printButton.className = 'print-btn';
        printButton.style.cssText = `
            margin-left: 10px;
            padding: 6px 12px;
            background: #17a2b8;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: background-color 0.3s ease;
        `;

        printButton.addEventListener('mouseenter', function () {
            this.style.backgroundColor = '#138496';
        });

        printButton.addEventListener('mouseleave', function () {
            this.style.backgroundColor = '#17a2b8';
        });

        printButton.addEventListener('click', function (e) {
            e.preventDefault();
            printKey(readonlyInput.value);
        });

        // 将打印按钮插入到复制按钮后面
        readonlyInput.parentNode.insertBefore(printButton, copyButton.nextSibling);
    }

    // 复制到剪贴板函数
    function copyToClipboard(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        textarea.setSelectionRange(0, 99999);

        try {
            const successful = document.writeText('copy');
            document.body.removeChild(textarea);

            if (successful) {
                showNotification('密钥已复制到剪贴板！', 'success');
            } else {
                showNotification('复制失败，请手动复制密钥。', 'error');
            }
        } catch (err) {
            document.body.removeChild(textarea);
            showNotification('复制失败，请手动复制密钥。', 'error');
            console.error('复制失败:', err);
        }
    }

    // 打印函数
    function printKey(key) {
        const printWindow = window.open('', '_blank');
        const printContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>NextDisk 加密密钥</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        text-align: center; 
                        padding: 50px; 
                        background: white;
                    }
                    .key-container { 
                        border: 2px solid #333; 
                        padding: 30px; 
                        margin: 20px auto; 
                        max-width: 600px;
                        background: #f9f9f9;
                    }
                    .key { 
                        font-family: monospace; 
                        font-size: 18px; 
                        font-weight: bold; 
                        color: #333;
                        word-break: break-all;
                    }
                    .warning { 
                        color: #d9534f; 
                        font-weight: bold; 
                        margin-top: 20px;
                    }
                    .timestamp {
                        color: #666;
                        margin-top: 20px;
                        font-size: 14px;
                    }
                    @media print {
                        body { padding: 0; }
                        .key-container { border: 3px solid #000; }
                    }
                </style>
            </head>
            <body>
                <h1>NextDisk 加密密钥</h1>
                <div class="key-container">
                    <div class="key">${key}</div>
                </div>
                <div class="warning">
                    ⚠️ 请务必将此密钥保存在安全的地方！若丢失密钥将无法解密文件。
                </div>
                <div class="timestamp">
                    生成时间: ${new Date().toLocaleString()}
                </div>
                <script>
                    window.onload = function() {
                        window.print();
                        setTimeout(function() {
                            window.close();
                        }, 500);
                    };
                </script>
            </body>
            </html>
        `;

        printWindow.document.write(printContent);
        printWindow.document.close();

        showNotification('正在打开打印对话框...', 'info');
    }

    // 显示通知函数
    function showNotification(message, type = 'info') {
        // 移除现有通知
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
            color: white;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            font-size: 14px;
            transition: all 0.3s ease;
        `;

        document.body.appendChild(notification);

        // 3秒后自动消失
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    console.log('All event listeners attached');
});