/**
 * Обработка AJAX запросов для лайков и отметки правильного ответа
 */

/**
 * Получить значение cookie по имени
 * @param {string} name - Имя cookie
 * @returns {string|null} Значение cookie или null
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Получить CSRF токен
 * @returns {string} CSRF токен
 */
function getCSRFToken() {
    const csrftoken = getCookie('csrftoken');
    if (!csrftoken) {
        console.error('CSRF token not found');
        return '';
    }
    return csrftoken;
}

/**
 * Лайк/дизлайк вопроса
 * @param {number} questionId - ID вопроса
 * @param {number} value - 1 для лайка, -1 для дизлайка
 * @param {HTMLElement} voteCountElement - Элемент для отображения рейтинга
 * @param {HTMLElement} clickedButton - Кнопка, на которую нажали
 */
function likeQuestion(questionId, value, voteCountElement, clickedButton) {
    const url = '/api/like/question/';
    const csrftoken = getCSRFToken();
    
    if (!csrftoken) {
        alert('Ошибка: CSRF токен не найден. Пожалуйста, обновите страницу.');
        return;
    }

    const formData = new FormData();
    formData.append('question_id', questionId);
    formData.append('value', value);
    formData.append('csrfmiddlewaretoken', csrftoken);

    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Ошибка при обработке запроса');
            });
        }
        return response.json();
    })
    .then(data => {
        if (voteCountElement) {
            voteCountElement.textContent = data.rating;
        }
        // Обновляем состояние кнопок с учетом нажатой кнопки
        updateVoteButtons(voteCountElement, data.removed, value, clickedButton);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка: ' + error.message);
    });
}

/**
 * Лайк/дизлайк ответа
 * @param {number} answerId - ID ответа
 * @param {number} value - 1 для лайка, -1 для дизлайка
 * @param {HTMLElement} voteCountElement - Элемент для отображения рейтинга
 * @param {HTMLElement} clickedButton - Кнопка, на которую нажали
 */
function likeAnswer(answerId, value, voteCountElement, clickedButton) {
    const url = '/api/like/answer/';
    const csrftoken = getCSRFToken();
    
    if (!csrftoken) {
        alert('Ошибка: CSRF токен не найден. Пожалуйста, обновите страницу.');
        return;
    }

    const formData = new FormData();
    formData.append('answer_id', answerId);
    formData.append('value', value);
    formData.append('csrfmiddlewaretoken', csrftoken);

    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Ошибка при обработке запроса');
            });
        }
        return response.json();
    })
    .then(data => {
        if (voteCountElement) {
            voteCountElement.textContent = data.rating;
        }
        // Обновляем состояние кнопок с учетом нажатой кнопки
        updateVoteButtons(voteCountElement, data.removed, value, clickedButton);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка: ' + error.message);
    });
}

/**
 * Отметить правильный ответ
 * @param {number} questionId - ID вопроса
 * @param {number} answerId - ID ответа
 * @param {boolean} isChecked - Состояние чекбокса
 * @param {HTMLElement} checkboxElement - Элемент чекбокса
 */
function markCorrectAnswer(questionId, answerId, isChecked, checkboxElement) {
    const url = '/api/mark-correct/';
    const csrftoken = getCSRFToken();
    
    if (!csrftoken) {
        alert('Ошибка: CSRF токен не найден. Пожалуйста, обновите страницу.');
        if (checkboxElement) {
            checkboxElement.checked = !isChecked; // Возвращаем предыдущее состояние
        }
        return;
    }

    const formData = new FormData();
    formData.append('question_id', questionId);
    formData.append('answer_id', answerId);
    formData.append('is_correct', isChecked);
    formData.append('csrfmiddlewaretoken', csrftoken);

    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Ошибка при обработке запроса');
            });
        }
        return response.json();
    })
    .then(data => {
        if (checkboxElement) {
            checkboxElement.checked = data.is_correct;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка: ' + error.message);
        // Возвращаем предыдущее состояние чекбокса при ошибке
        if (checkboxElement) {
            checkboxElement.checked = !isChecked;
        }
    });
}

/**
 * Обновить состояние кнопок голосования
 * @param {HTMLElement} voteCountElement - Элемент с рейтингом
 * @param {boolean} removed - Был ли лайк удален
 * @param {number} value - Значение голоса (1 для лайка, -1 для дизлайка)
 * @param {HTMLElement} clickedButton - Кнопка, на которую нажали
 */
function updateVoteButtons(voteCountElement, removed, value, clickedButton) {
    if (!voteCountElement) return;
    
    const votingControls = voteCountElement.closest('.voting-controls');
    if (!votingControls) return;
    
    const voteUpBtn = votingControls.querySelector('.vote-up');
    const voteDownBtn = votingControls.querySelector('.vote-down');
    
    // Убираем классы active с обеих кнопок
    if (voteUpBtn) voteUpBtn.classList.remove('active', 'vote-up-active');
    if (voteDownBtn) voteDownBtn.classList.remove('active', 'vote-down-active');
    
    if (removed) {
        // Лайк был удален - возвращаем кнопки в исходное состояние
        // Классы уже удалены выше
    } else {
        // Лайк был установлен - окрашиваем соответствующую кнопку
        if (value === 1 && voteUpBtn) {
            // Лайк установлен - окрашиваем кнопку "+" в зеленый
            voteUpBtn.classList.add('active', 'vote-up-active');
        } else if (value === -1 && voteDownBtn) {
            // Дизлайк установлен - окрашиваем кнопку "-" в красный
            voteDownBtn.classList.add('active', 'vote-down-active');
        }
    }
}

// Инициализация обработчиков событий после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    // Обработчики для лайков вопросов
    document.querySelectorAll('.question-voting .vote-up, .question-voting .vote-down').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const votingControls = this.closest('.voting-controls');
            if (!votingControls) return;
            
            const questionItem = this.closest('.question-item');
            if (!questionItem) return;
            
            const questionId = questionItem.dataset.questionId;
            if (!questionId) return;
            
            const voteCountElement = votingControls.querySelector('.vote-count');
            const value = this.classList.contains('vote-up') ? 1 : -1;
            
            likeQuestion(parseInt(questionId), value, voteCountElement, this);
        });
    });
    
    // Обработчики для лайков ответов
    document.querySelectorAll('.answer-voting .vote-up, .answer-voting .vote-down').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const votingControls = this.closest('.voting-controls');
            if (!votingControls) return;
            
            const answerItem = this.closest('.answer-item');
            if (!answerItem) return;
            
            const answerId = answerItem.dataset.answerId;
            if (!answerId) return;
            
            const voteCountElement = votingControls.querySelector('.vote-count');
            const value = this.classList.contains('vote-up') ? 1 : -1;
            
            likeAnswer(parseInt(answerId), value, voteCountElement, this);
        });
    });
    
    // Обработчик для чекбокса правильного ответа
    document.querySelectorAll('.correct-answer input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const answerItem = this.closest('.answer-item');
            if (!answerItem) return;
            
            const questionId = answerItem.dataset.questionId;
            const answerId = answerItem.dataset.answerId;
            
            if (!questionId || !answerId) return;
            
            markCorrectAnswer(parseInt(questionId), parseInt(answerId), this.checked, this);
        });
    });
});

