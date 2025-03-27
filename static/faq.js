// Accordion Functionality
const faqQuestions = document.querySelectorAll('.faq-question');
faqQuestions.forEach((question) => {
  question.addEventListener('click', () => {
    const answer = question.nextElementSibling;

    if (answer.classList.contains('open')) {
      answer.classList.remove('open');
      question.querySelector('span').textContent = '+';
    } else {
      document.querySelectorAll('.faq-answer').forEach((ans) => ans.classList.remove('open'));
      faqQuestions.forEach((q) => q.querySelector('span').textContent = '+');

      answer.classList.add('open');
      question.querySelector('span').textContent = '-';
    }
  });
});

// FAQ Grid Functionality
document.querySelectorAll('.faq-box').forEach(box => {
  box.addEventListener('click', () => {
    const faqId = box.getAttribute('data-faq');
    const faqContent = document.getElementById(faqId);
    document.querySelectorAll('.faq-content').forEach(content => content.style.display = 'none');
    if (faqContent) faqContent.style.display = 'block';
  });
});
