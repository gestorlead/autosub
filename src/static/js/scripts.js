// Scripts para a aplicação AutoSub

document.addEventListener('DOMContentLoaded', function() {
    
    // Inicializa tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Verifica atualizações automáticas para vídeos em processamento
    const videoStatusElement = document.querySelector('.video-status-processing');
    if (videoStatusElement) {
        setInterval(function() {
            window.location.reload();
        }, 30000); // Recarrega a cada 30 segundos
    }
    
    // Funcionalidade de arrastar e soltar para upload de arquivos
    const dropZone = document.querySelector('.drop-zone');
    const fileInput = document.querySelector('.drop-zone-input');
    
    if (dropZone && fileInput) {
        dropZone.addEventListener('click', () => {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', (e) => {
            if (fileInput.files.length) {
                updateDropZone(fileInput.files[0]);
            }
        });
        
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('active');
        });
        
        ['dragleave', 'dragend'].forEach((type) => {
            dropZone.addEventListener(type, () => {
                dropZone.classList.remove('active');
            });
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                updateDropZone(e.dataTransfer.files[0]);
            }
            
            dropZone.classList.remove('active');
        });
        
        // Atualiza a interface quando um arquivo é selecionado
        function updateDropZone(file) {
            let fileNameElement = dropZone.querySelector('.drop-zone-prompt');
            
            if (fileNameElement) {
                fileNameElement.textContent = file.name;
            } else {
                const span = document.createElement('span');
                span.className = 'drop-zone-prompt';
                span.textContent = file.name;
                dropZone.appendChild(span);
            }
            
            if (!dropZone.querySelector('.drop-zone-thumb')) {
                const thumbnail = document.createElement('div');
                thumbnail.className = 'drop-zone-thumb';
                dropZone.appendChild(thumbnail);
            }
            
            // Para vídeos, poderíamos tentar gerar uma miniatura, mas isso requer mais código
        }
    }
    
    // Confirmação para exclusão
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Tem certeza que deseja excluir este item?')) {
                e.preventDefault();
            }
        });
    });
    
    // Validação de formulários
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Verificação de senhas coincidentes
    const password = document.getElementById('new_password');
    const confirmPassword = document.getElementById('confirm_password');
    
    if (password && confirmPassword) {
        function validatePassword() {
            if (password.value !== confirmPassword.value) {
                confirmPassword.setCustomValidity('As senhas não coincidem');
            } else {
                confirmPassword.setCustomValidity('');
            }
        }
        
        password.addEventListener('change', validatePassword);
        confirmPassword.addEventListener('keyup', validatePassword);
    }
    
    // Contador de caracteres para campos de texto
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(textarea => {
        const counter = document.createElement('div');
        counter.className = 'text-muted small text-end';
        counter.innerHTML = `<span class="char-count">${textarea.value.length}</span>/${textarea.maxLength}`;
        textarea.parentNode.insertBefore(counter, textarea.nextSibling);
        
        textarea.addEventListener('input', function() {
            const count = this.value.length;
            this.nextSibling.querySelector('.char-count').textContent = count;
            
            if (count > this.maxLength * 0.9) {
                this.nextSibling.classList.add('text-danger');
            } else {
                this.nextSibling.classList.remove('text-danger');
            }
        });
    });
    
    // Botões para copiar texto para a área de transferência
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const platform = this.getAttribute('data-content');
            const textElement = document.getElementById(`${platform}-text`);
            
            if (textElement) {
                navigator.clipboard.writeText(textElement.textContent.trim())
                    .then(() => {
                        // Feedback visual de sucesso
                        const originalText = this.innerHTML;
                        this.innerHTML = '<i class="fas fa-check me-1"></i>Copiado!';
                        this.classList.remove('btn-outline-primary');
                        this.classList.add('btn-success');
                        
                        setTimeout(() => {
                            this.innerHTML = originalText;
                            this.classList.remove('btn-success');
                            this.classList.add('btn-outline-primary');
                        }, 2000);
                    })
                    .catch(err => {
                        console.error('Erro ao copiar texto: ', err);
                        alert('Não foi possível copiar o texto. Por favor, tente novamente.');
                    });
            }
        });
    });
    
    // Botões para gerar conteúdo de redes sociais
    const generateButtons = document.querySelectorAll('.generate-social');
    generateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const platform = this.getAttribute('data-platform');
            const videoId = window.location.pathname.split('/').pop();
            
            // Desabilita o botão e mostra indicador de carregamento
            this.disabled = true;
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Gerando...';
            
            // Faz a solicitação AJAX
            fetch(`/video/${videoId}/generate-social?platform=${platform}`)
                .then(response => response.json())
                .then(data => {
                    // Recarrega a página para mostrar o conteúdo gerado
                    window.location.reload();
                })
                .catch(error => {
                    console.error('Erro ao gerar conteúdo:', error);
                    this.disabled = false;
                    this.innerHTML = originalText;
                    alert('Ocorreu um erro ao gerar o conteúdo. Por favor, tente novamente.');
                });
        });
    });
}); 