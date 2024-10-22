document.addEventListener('DOMContentLoaded', () => {
  fetch('data/activity.json')
    .then(response => response.json())
    .then(jsonData => {
      console.log(jsonData);
      let activity_object = jsonData;

      // Render image
      document.querySelector('.image').innerHTML = `<img id="target_image" src="${activity_object.media.image_src}" alt="Image">`;
      document.getElementById('image_container').addEventListener('click', () => {
        window.open(activity_object.media.image_src, '_blank');
      });

      // Render sentence
      document.getElementById('sentence').textContent = `${activity_object.sentence}`;

      // Render questions
      const questionsContainer = document.getElementById('questions_container');
      const questions = activity_object.questions;

      for (let key in questions) {
        if (questions.hasOwnProperty(key)) {
          const questionDiv = document.createElement('div');
          questionDiv.className = 'question_div';
          questionDiv.onclick = () => toggleAnswer(`answer_${key}`);

          const questionText = document.createElement('span');
          questionText.className = 'question';
          questionText.id = `question_${key}`;
          questionText.textContent = questions[key].sentence;

          const answerText = document.createElement('div');
          answerText.className = 'answer';
          answerText.id = `answer_${key}`;
          answerText.textContent = questions[key].answer;

          questionDiv.appendChild(questionText);
          questionDiv.appendChild(answerText);
          questionsContainer.appendChild(questionDiv);
        }
      }

      // Render options
      document.getElementById('option_a').textContent = `${activity_object.options.A}`;
      document.getElementById('option_b').textContent = `${activity_object.options.B}`;
      document.getElementById('option_c').textContent = `${activity_object.options.C}`;
      document.getElementById('option_d').textContent = `${activity_object.options.D}`;

      // Add event listeners for options
      const addOptionClickListener = (optionDiv, optionSpan, userChoice) => {
        optionDiv.addEventListener('click', () => {
          const correctAnswer = activity_object.correct_answer.toUpperCase();
          if (userChoice === correctAnswer) {
            optionSpan.style.backgroundColor = '#8CC63F';
            optionSpan.style.color = 'white';
            optionDiv.style.backgroundColor = '#8CC63F';
            setTimeout(() => {
              location.reload();
            }, 2000);
          } else {
            optionSpan.style.backgroundColor = 'white';
            optionSpan.style.color = '#D32B45';
            optionSpan.style.textDecoration = 'line-through';
          }
        });
      };

      addOptionClickListener(document.getElementById('option_a_div'), document.getElementById('option_a'), 'A');
      addOptionClickListener(document.getElementById('option_b_div'), document.getElementById('option_b'), 'B');
      addOptionClickListener(document.getElementById('option_c_div'), document.getElementById('option_c'), 'C');
      addOptionClickListener(document.getElementById('option_d_div'), document.getElementById('option_d'), 'D');
    })
    .catch(error => {
      console.error('Error fetching data:', error);
    });
});

function toggleAnswer(answerId) {
  const answerElement = document.getElementById(answerId);
  if (answerElement.style.display === 'none' || answerElement.style.display === '') {
    answerElement.style.display = 'block';
  } else {
    answerElement.style.display = 'none';
  }
}