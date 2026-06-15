/**
 * NutriPrint pilot workspace
 * Provides realistic school records for screenshot capture, viva walkthroughs,
 * and offline project expo review without exposing implementation scaffolding
 * in the product UI.
 */

'use strict';

(function () {
  const SESSION_KEY = 'np_teacher_session';
  const PILOT_FLAG = 'np_pilot_workspace';

  const PILOT_SESSION = {
    email: 'kavya.rao@nutriprint.in',
    name: 'Kavya Rao',
    school: 'Government Higher Primary School, Moodbidri',
    district: 'Dakshina Kannada',
    loggedInAt: Date.now(),
    isPilot: true,
  };

  const PILOT_STUDENTS = [
    { name: 'Aarav Hegde', age: 11, gender: 'boy', bmi: 16.9, classification: 'normal' },
    { name: 'Nisha Poojary', age: 10, gender: 'girl', bmi: 14.5, classification: 'underweight' },
    { name: 'Kiran Gowda', age: 12, gender: 'boy', bmi: 19.6, classification: 'normal' },
    { name: 'Meera Naik', age: 13, gender: 'girl', bmi: 25.0, classification: 'overweight' },
    { name: 'Samarth Shetty', age: 9, gender: 'boy', bmi: 14.2, classification: 'underweight' },
    { name: "Anika D'Souza", age: 11, gender: 'girl', bmi: 17.6, classification: 'normal' },
  ];

  const PILOT_HISTORY = {
    'Aarav Hegde': [
      { date: '10/04/2026', bmi: 16.2, classification: 'normal', label: 'Baseline', age: 11, gender: 'boy' },
      { date: '10/05/2026', bmi: 16.6, classification: 'normal', label: 'Month 1', age: 11, gender: 'boy' },
      { date: '10/06/2026', bmi: 16.9, classification: 'normal', label: 'Month 2', age: 11, gender: 'boy' },
    ],
    'Nisha Poojary': [
      { date: '12/04/2026', bmi: 13.8, classification: 'underweight', label: 'Baseline', age: 10, gender: 'girl' },
      { date: '12/05/2026', bmi: 14.1, classification: 'underweight', label: 'Month 1', age: 10, gender: 'girl' },
      { date: '12/06/2026', bmi: 14.5, classification: 'underweight', label: 'Month 2', age: 10, gender: 'girl' },
    ],
    'Kiran Gowda': [
      { date: '08/04/2026', bmi: 19.0, classification: 'normal', label: 'Baseline', age: 12, gender: 'boy' },
      { date: '08/05/2026', bmi: 19.3, classification: 'normal', label: 'Month 1', age: 12, gender: 'boy' },
      { date: '08/06/2026', bmi: 19.6, classification: 'normal', label: 'Month 2', age: 12, gender: 'boy' },
    ],
    'Meera Naik': [
      { date: '15/04/2026', bmi: 25.9, classification: 'overweight', label: 'Baseline', age: 13, gender: 'girl' },
      { date: '15/05/2026', bmi: 25.4, classification: 'overweight', label: 'Month 1', age: 13, gender: 'girl' },
      { date: '15/06/2026', bmi: 25.0, classification: 'overweight', label: 'Month 2', age: 13, gender: 'girl' },
    ],
    'Samarth Shetty': [
      { date: '18/04/2026', bmi: 13.7, classification: 'underweight', label: 'Baseline', age: 9, gender: 'boy' },
      { date: '18/05/2026', bmi: 14.0, classification: 'underweight', label: 'Month 1', age: 9, gender: 'boy' },
      { date: '18/06/2026', bmi: 14.2, classification: 'underweight', label: 'Month 2', age: 9, gender: 'boy' },
    ],
    "Anika D'Souza": [
      { date: '20/04/2026', bmi: 17.1, classification: 'normal', label: 'Baseline', age: 11, gender: 'girl' },
      { date: '20/05/2026', bmi: 17.4, classification: 'normal', label: 'Month 1', age: 11, gender: 'girl' },
      { date: '13/06/2026', bmi: 17.6, classification: 'normal', label: 'Month 2', age: 11, gender: 'girl' },
    ],
  };

  const PILOT_STATS = {
    total_students: 38,
    total_plans: 31,
    total_assessments: 38,
    total_foods: 72,
    plans_this_month: 12,
    teacher_name: 'Kavya Rao',
    school_name: 'Government Higher Primary School, Moodbidri',
  };

  function seed() {
    Object.entries(PILOT_HISTORY).forEach(([name, records]) => {
      localStorage.setItem('bmi_history_' + name, JSON.stringify(records));
    });
    ['pilot-plan-aarav', 'pilot-plan-nisha', 'pilot-plan-meera'].forEach(token => {
      localStorage.setItem('meal_plan_' + token, '1');
    });
    localStorage.setItem('teacher_id', 'pilot-teacher-moodbidri');
    localStorage.setItem('np_pilot_stats', JSON.stringify(PILOT_STATS));
    localStorage.setItem('nutriprint_last_bmi', JSON.stringify({
      student_name: 'Nisha Poojary',
      age: 10,
      gender: 'girl',
      height_cm: 134,
      weight_kg: 26,
      bmi_value: 14.5,
      classification: 'underweight',
      percentile: 7,
      z_score: -1.8,
      advice_en: 'Nisha is underweight. Increase calorie and protein intake using ragi mudde, horsegram saaru, curd rice, and groundnut laddu.',
      advice_kn: 'ನಿಶಾ ತೂಕ ಕಡಿಮೆ ವರ್ಗದಲ್ಲಿದ್ದಾರೆ. ರಾಗಿ ಮುದ್ದೆ, ಹುರಳಿ ಸಾರು, ಮೊಸರು ಅನ್ನ ಮತ್ತು ಕಡಲೆ ಉಂಡೆ ಸೇರಿಸಿ.',
    }));
    localStorage.setItem(PILOT_FLAG, '1');
  }

  function clean() {
    Object.keys(PILOT_HISTORY).forEach(name => localStorage.removeItem('bmi_history_' + name));
    ['pilot-plan-aarav', 'pilot-plan-nisha', 'pilot-plan-meera'].forEach(token => {
      localStorage.removeItem('meal_plan_' + token);
    });
    localStorage.removeItem('np_pilot_stats');
    localStorage.removeItem('nutriprint_last_bmi');
    localStorage.removeItem(PILOT_FLAG);
  }

  function isActive() {
    return localStorage.getItem(PILOT_FLAG) === '1';
  }

  function activate() {
    localStorage.setItem(SESSION_KEY, JSON.stringify(PILOT_SESSION));
    seed();
    window.location.replace('/dashboard');
  }

  function exit() {
    if (typeof NutriAuth !== 'undefined') NutriAuth.logout();
    clean();
    window.location.replace('/login');
  }

  function getStudents() {
    return PILOT_STUDENTS.map(s => ({
      name: s.name,
      age: s.age,
      gender: s.gender,
      last_bmi: s.bmi,
      classification: s.classification,
      last_assessed: (PILOT_HISTORY[s.name] || []).slice(-1)[0]?.date || '-',
    }));
  }

  function getStats() {
    return PILOT_STATS;
  }

  window.NutriPilot = { isActive, activate, exit, getStudents, getStats };
})();
