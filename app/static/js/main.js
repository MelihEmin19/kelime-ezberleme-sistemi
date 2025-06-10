// Ana JavaScript dosyası

document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap bileşenlerini aktif et
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Flash mesajları için otomatik kapanma
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            alert.classList.add('fade');
            setTimeout(function() {
                alert.remove();
            }, 500);
        });
    }, 3000); // 3 saniye sonra

    // Çalışma kartları için klavye kısayolları
    document.addEventListener('keydown', function(event) {
        if (event.target.tagName.toLowerCase() !== 'input' && event.target.tagName.toLowerCase() !== 'textarea') {
            // Sonraki kelimeye geçmek için sağ ok tuşu
            if (event.key === 'ArrowRight') {
                const nextButton = document.querySelector('.next-word-btn');
                if (nextButton) {
                    nextButton.click();
                }
            }
            
            // Önceki kelimeye geçmek için sol ok tuşu
            if (event.key === 'ArrowLeft') {
                const prevButton = document.querySelector('.prev-word-btn');
                if (prevButton) {
                    prevButton.click();
                }
            }
        }
    });

    // Kelime çalışması için form doğrulama
    const studyForm = document.querySelector('.study-form');
    if (studyForm) {
        studyForm.addEventListener('submit', function(event) {
            const answerInput = document.getElementById('answer');
            if (answerInput && answerInput.value.trim() === '') {
                event.preventDefault();
                answerInput.classList.add('is-invalid');
            }
        });
    }
});