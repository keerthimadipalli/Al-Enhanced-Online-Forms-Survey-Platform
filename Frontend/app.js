// app.js – shared utilities for FormFlow

function showToast(msg) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2800);
}

function requireLogin() {
  const user = localStorage.getItem('user');
  if (!user) window.location.href = 'login.html';
}

function getUser() {
  return JSON.parse(localStorage.getItem('user') || '{}');
}

// Seed some demo data if empty
(function seedDemo() {
  const forms = JSON.parse(localStorage.getItem('ff_forms') || '[]');
  if (forms.length > 0) return;

  const demo = [
    {
      id: 'f_demo1',
      title: 'Customer Satisfaction Survey',
      description: 'How was your experience with our service?',
      category: 'feedback',
      questions: [
        { text: 'How satisfied are you overall?', type: 'rating', required: true, options: [] },
        { text: 'What did you like most?', type: 'text', required: false, options: [] },
        { text: 'Would you recommend us?', type: 'mcq', required: true, options: ['Yes', 'Maybe', 'No'] },
        { text: 'Any suggestions for improvement?', type: 'text', required: false, options: [] }
      ],
      responses: 3,
      created_at: new Date(Date.now() - 86400000 * 2).toISOString()
    },
    {
      id: 'f_demo2',
      title: 'Event Feedback Form',
      description: 'We want to hear about your experience at our workshop.',
      category: 'event',
      questions: [
        { text: 'How would you rate the event?', type: 'rating', required: true, options: [] },
        { text: 'What was the best part?', type: 'text', required: false, options: [] },
        { text: 'How was the venue?', type: 'mcq', required: false, options: ['Excellent', 'Good', 'Average', 'Poor'] }
      ],
      responses: 1,
      created_at: new Date(Date.now() - 86400000).toISOString()
    }
  ];

  localStorage.setItem('ff_forms', JSON.stringify(demo));

  // Seed some responses for demo1
  const resp1 = [
    { form_id: 'f_demo1', answers: { q0: '4', q1: 'Very helpful support team', q2: 'Yes', q3: 'Maybe a faster response time' }, submitted_at: new Date(Date.now() - 3600000 * 5).toISOString() },
    { form_id: 'f_demo1', answers: { q0: '5', q1: 'Amazing experience overall, great service', q2: 'Yes', q3: '' }, submitted_at: new Date(Date.now() - 3600000 * 10).toISOString() },
    { form_id: 'f_demo1', answers: { q0: '2', q1: 'Nothing really', q2: 'No', q3: 'Too slow and confusing' }, submitted_at: new Date(Date.now() - 3600000 * 20).toISOString() },
  ];
  localStorage.setItem('ff_resp_f_demo1', JSON.stringify(resp1));
  localStorage.setItem('ff_resp_f_demo2', JSON.stringify([
    { form_id: 'f_demo2', answers: { q0: '5', q1: 'Great speakers', q2: 'Excellent' }, submitted_at: new Date().toISOString() }
  ]));
})();
