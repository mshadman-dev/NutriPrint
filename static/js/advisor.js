(function () {
  const AGE_WATER_GUIDANCE = [
    { min: 1, max: 3, labelEn: '1–3 years', labelKn: '1–3 ವರ್ಷ', valueEn: '1.3 L/day', valueKn: '1.3 ಲೀ/ದಿನ' },
    { min: 4, max: 8, labelEn: '4–8 years', labelKn: '4–8 ವರ್ಷ', valueEn: '1.7 L/day', valueKn: '1.7 ಲೀ/ದಿನ' },
    { min: 9, max: 13, labelEn: '9–13 years', labelKn: '9–13 ವರ್ಷ', valueEn: '2.1–2.4 L/day', valueKn: '2.1–2.4 ಲೀ/ದಿನ' },
    { min: 14, max: 18, labelEn: '14–18 years', labelKn: '14–18 ವರ್ಷ', valueEn: '2.3–3.3 L/day', valueKn: '2.3–3.3 ಲೀ/ದಿನ' },
  ];

  const CATEGORY_RULES = {
    underweight: {
      titleEn: 'Healthy weight gain focus',
      titleKn: 'ಆರೋಗ್ಯಕರ ತೂಕ ಹೆಚ್ಚಿಸುವ ಗಮನ',
      summaryEn: 'Build weight gradually with calorie-dense, protein-rich foods and regular meals.',
      summaryKn: 'ಕ್ಯಾಲರಿ ಸಮೃದ್ಧ ಮತ್ತು ಪ್ರೋಟೀನ್ ಆಹಾರಗಳೊಂದಿಗೆ ನಿಯಮಿತ ಊಟದಿಂದ ತೂಕವನ್ನು ನಿಧಾನವಾಗಿ ಹೆಚ್ಚಿಸಿ.',
      activityEn: 'Light play, stretching, and supervised movement for 45–60 minutes daily.',
      activityKn: 'ಪ್ರತಿದಿನ 45–60 ನಿಮಿಷ ಹಗುರವಾದ ಆಟ, ಸ್ಟ್ರೆಚಿಂಗ್ ಮತ್ತು ಮೇಲ್ವಿಚಾರಿತ ಚಟುವಟಿಕೆ.',
      snackEn: 'Add milk, eggs, banana, peanut chikki, and dal-based snacks.',
      snackKn: 'ಹಾಲು, ಮೊಟ್ಟೆ, ಬಾಳೆಹಣ್ಣು, ಕಡಲೆಕಾಯಿ ಚಿಕ್ಕಿ, ಮತ್ತು ಬೇಳೆ ಆಧಾರಿತ ಸ್ನ್ಯಾಕ್ಸ್ ಸೇರಿಸಿ.',
    },
    normal: {
      titleEn: 'Balanced nutrition maintenance',
      titleKn: 'ಸಮತೋಲನ ಆಹಾರವನ್ನು ಮುಂದುವರಿಸಿ',
      summaryEn: 'Keep the current range with balanced meals, hydration, and regular activity.',
      summaryKn: 'ಸಮತೋಲನ ಆಹಾರ, ನೀರಿನ ಸೇವನೆ ಮತ್ತು ನಿಯಮಿತ ಚಟುವಟಿಕೆಯಿಂದ ಪ್ರಸ್ತುತ ಮಟ್ಟವನ್ನು ಕಾಯ್ದುಕೊಳ್ಳಿ.',
      activityEn: 'Aim for 60 minutes of mixed movement and outdoor play daily.',
      activityKn: 'ಪ್ರತಿದಿನ 60 ನಿಮಿಷ ಮಿಶ್ರ ಚಟುವಟಿಕೆ ಮತ್ತು ಹೊರಾಂಗಣ ಆಟಕ್ಕೆ ಪ್ರಯತ್ನಿಸಿ.',
      snackEn: 'Choose fruits, sprouts, curd, and roasted groundnuts between meals.',
      snackKn: 'ಊಟಗಳ ನಡುವೆ ಹಣ್ಣು, ಮೊಳಕೆಕಾಳು, ಮೊಸರು ಮತ್ತು ಹುರಿದ ಕಡಲೆಕಾಯಿ ಆಯ್ಕೆಮಾಡಿ.',
    },
    overweight: {
      titleEn: 'Healthy weight control',
      titleKn: 'ಆರೋಗ್ಯಕರ ತೂಕ ನಿಯಂತ್ರಣ',
      summaryEn: 'Reduce processed foods, tighten portions, and prioritize fiber-rich meals.',
      summaryKn: 'ಪ್ರೊಸೆಸ್ಡ್ ಆಹಾರ ಕಡಿಮೆ ಮಾಡಿ, ಭಾಗಗಳನ್ನು ನಿಯಂತ್ರಿಸಿ, ಮತ್ತು ನಾರುಪೂರಿತ ಊಟಗಳನ್ನು ಹೆಚ್ಚಿಸಿ.',
      activityEn: 'Include brisk walking, cycling, and active games for at least 60 minutes daily.',
      activityKn: 'ಪ್ರತಿದಿನ ಕನಿಷ್ಠ 60 ನಿಮಿಷ ಚುರುಕಿನ ನಡೆ, ಸೈಕ್ಲಿಂಗ್ ಮತ್ತು ಚುರುಕಿನ ಆಟಗಳು.',
      snackEn: 'Replace packaged snacks with fruit, roasted chana, and buttermilk.',
      snackKn: 'ಪ್ಯಾಕೇಜ್ಡ್ ಸ್ನ್ಯಾಕ್ಸ್‌ಗಳ ಬದಲು ಹಣ್ಣು, ಹುರಿದ ಕಡಲೆ ಮತ್ತು ಮಜ್ಜಿಗೆ ಬಳಸಿ.',
    },
    obese: {
      titleEn: 'Portion-aware recovery plan',
      titleKn: 'ಭಾಗ ನಿಯಂತ್ರಣದ ಸುಧಾರಣಾ ಯೋಜನೆ',
      summaryEn: 'Focus on portion control, healthy snack swaps, and steady daily movement.',
      summaryKn: 'ಭಾಗ ನಿಯಂತ್ರಣ, ಆರೋಗ್ಯಕರ ಸ್ನ್ಯಾಕ್ ಬದಲಾವಣೆ, ಮತ್ತು ನಿರಂತರ ಚಟುವಟಿಕೆಗೆ ಗಮನ ಕೊಡಿ.',
      activityEn: 'Target 60–90 minutes of movement daily, broken into school-friendly sessions.',
      activityKn: 'ಪ್ರತಿದಿನ 60–90 ನಿಮಿಷ ಚಟುವಟಿಕೆ, ಶಾಲೆಗೆ ಹೊಂದುವ ಚಿಕ್ಕ ಸೆಷನ್‌ಗಳಲ್ಲಿ ಹಂಚಿ.',
      snackEn: 'Use fruit, sprouts, curd, and lightly spiced home snacks instead of fried food.',
      snackKn: 'ಹುರಿದ ತಿಂಡಿಗಳ ಬದಲು ಹಣ್ಣು, ಮೊಳಕೆಕಾಳು, ಮೊಸರು, ಮತ್ತು ಕಡಿಮೆ ಮಸಾಲೆಯ ಮನೆಸ್ನ್ಯಾಕ್ ಬಳಸಿ.',
    },
  };

  const KARNATAKA_FOODS = [
    { en: 'Ragi Mudde', kn: 'ರಾಗಿ ಮುದ್ದೆ' },
    { en: 'Ragi Dosa', kn: 'ರಾಗಿ ದೋಸೆ' },
    { en: 'Jowar Roti', kn: 'ಜೋಳದ ರೊಟ್ಟಿ' },
    { en: 'Coconut Rice', kn: 'ತೆಂಗಿನಕಾಯಿ ಅನ್ನ' },
    { en: 'Green Gram', kn: 'ಹೆಸರುಕಾಳು' },
    { en: 'Groundnuts', kn: 'ಕಡಲೆಕಾಯಿ' },
    { en: 'Milk', kn: 'ಹಾಲು' },
    { en: 'Eggs', kn: 'ಮೊಟ್ಟೆಗಳು' },
  ];

  const WEEKLY_GOALS = [
    { en: 'Drink 2L water daily', kn: 'ಪ್ರತಿದಿನ 2 ಲೀಟರ್ ನೀರು ಕುಡಿಯಿರಿ' },
    { en: 'Eat fruits 5 times per week', kn: 'ವಾರದಲ್ಲಿ 5 ಬಾರಿ ಹಣ್ಣುಗಳನ್ನು ತಿನ್ನಿರಿ' },
    { en: 'Consume protein in every meal', kn: 'ಪ್ರತಿ ಊಟದಲ್ಲೂ ಪ್ರೋಟೀನ್ ಸೇರಿಸಿ' },
    { en: 'Reduce packaged snacks', kn: 'ಪ್ಯಾಕೇಜ್ಡ್ ಸ್ನ್ಯಾಕ್ಸ್ ಕಡಿಮೆ ಮಾಡಿ' },
  ];

  function escapeHtml(value) {
    return String(value ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
  }

  function toNumber(value) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }

  function ageLabel(age) {
    const numericAge = toNumber(age);
    if (numericAge == null) {
      return AGE_WATER_GUIDANCE[2];
    }
    return AGE_WATER_GUIDANCE.find((bucket) => numericAge >= bucket.min && numericAge <= bucket.max) || AGE_WATER_GUIDANCE[2];
  }

  function formatGender(gender) {
    if (!gender) return { en: 'Not specified', kn: 'ನಿರ್ದಿಷ್ಟಪಡಿಸಿಲ್ಲ' };
    if (gender === 'girl') return { en: 'Girl', kn: 'ಹುಡುಗಿ' };
    if (gender === 'boy') return { en: 'Boy', kn: 'ಹುಡುಗ' };
    return { en: String(gender), kn: String(gender) };
  }

  function mealText(plan) {
    if (!plan?.week?.length) return '';
    return plan.week
      .map((day) => [day.breakfast, day.lunch, day.dinner]
        .map((meal) => [meal?.name_en, meal?.name_kn, ...(meal?.ingredients || [])].join(' '))
        .join(' '))
      .join(' ')
      .toLowerCase();
  }

  function countMatches(text, keywords) {
    return keywords.reduce((count, keyword) => count + (text.includes(keyword) ? 1 : 0), 0);
  }

  function buildMealSignals(plan) {
    const text = mealText(plan);
    return {
      protein: countMatches(text, ['egg', 'eggs', 'milk', 'paneer', 'dal', 'moong', 'green gram', 'groundnut', 'nuts', 'chicken', 'fish']),
      iron: countMatches(text, ['ragi', 'greens', 'spinach', 'dal', 'groundnut', 'egg', 'beans', 'millet']),
      fiber: countMatches(text, ['vegetable', 'vegetables', 'fruit', 'fruits', 'ragi', 'jowar', 'sprout', 'sprouts', 'brown rice', 'millet']),
      hydration: countMatches(text, ['curd', 'buttermilk', 'milk', 'fruit', 'watermelon', 'cucumber']),
    };
  }

  function riskLevel(level) {
    return level === 'high' || level === 'medium' || level === 'low' ? level : 'low';
  }

  function buildRiskProfile(model) {
    const planSignals = buildMealSignals(model.plan);
    const category = model.bmiCategory;
    const age = model.age;

    const proteinRisk = category === 'underweight' || planSignals.protein < 3
      ? 'high'
      : planSignals.protein < 5
        ? 'medium'
        : 'low';

    const ironRisk = (model.gender === 'girl' && age >= 9) || category === 'underweight' || planSignals.iron < 3
      ? 'medium'
      : planSignals.iron < 5
        ? 'low'
        : 'low';

    const hydrationRisk = age >= 14 || category === 'overweight' || category === 'obese'
      ? 'medium'
      : 'low';

    const fiberRisk = category === 'overweight' || category === 'obese' || planSignals.fiber < 4
      ? 'high'
      : planSignals.fiber < 6
        ? 'medium'
        : 'low';

    return {
      iron: {
        level: riskLevel(ironRisk),
        titleEn: 'Iron deficiency risk',
        titleKn: 'ಕಬ್ಬಿಣ ಕೊರತೆ ಅಪಾಯ',
        bodyEn: category === 'underweight'
          ? 'Include ragi, greens, dal, and groundnuts to support red blood cell health.'
          : 'Girls aged 9+ and students with light meals should get ragi, greens, dal, and groundnuts.',
        bodyKn: category === 'underweight'
          ? 'ರಾಗಿ, ಹಸಿರು ಸೊಪ್ಪು, ಬೇಳೆ ಮತ್ತು ಕಡಲೆಕಾಯಿ ಸೇರಿಸಿ.'
          : '9 ವರ್ಷ ಮೇಲ್ಪಟ್ಟ ಹುಡುಗಿಯರು ಮತ್ತು ಹಗುರವಾದ ಊಟ ಪಡೆಯುವ ವಿದ್ಯಾರ್ಥಿಗಳಿಗೆ ರಾಗಿ, ಸೊಪ್ಪು, ಬೇಳೆ, ಕಡಲೆಕಾಯಿ ಸೇರಿಸಿ.',
      },
      protein: {
        level: riskLevel(proteinRisk),
        titleEn: 'Protein deficiency risk',
        titleKn: 'ಪ್ರೋಟೀನ್ ಕೊರತೆ ಅಪಾಯ',
        bodyEn: category === 'underweight'
          ? 'Boost protein at every meal with milk, eggs, dal, paneer, and green gram.'
          : 'Keep protein steady with dal, milk, eggs, paneer, and sprouts in each meal.'
          ,
        bodyKn: category === 'underweight'
          ? 'ಪ್ರತಿ ಊಟದಲ್ಲೂ ಹಾಲು, ಮೊಟ್ಟೆ, ಬೇಳೆ, ಪನೀರ್ ಮತ್ತು ಹೆಸರುಕಾಳು ಸೇರಿಸಿ.'
          : 'ಪ್ರತಿ ಊಟದಲ್ಲೂ ಬೇಳೆ, ಹಾಲು, ಮೊಟ್ಟೆ, ಪನೀರ್ ಮತ್ತು ಮೊಳಕೆಕಾಳು ಸೇರಿಸಿ.',
      },
      hydration: {
        level: riskLevel(hydrationRisk),
        titleEn: 'Low hydration risk',
        titleKn: 'ಕಡಿಮೆ ನೀರಿನ ಸೇವನೆ ಅಪಾಯ',
        bodyEn: 'Send a water bottle to school and sip regularly between classes and meals.',
        bodyKn: 'ಶಾಲೆಗೆ ನೀರಿನ ಬಾಟಲಿ ಕಳುಹಿಸಿ ಮತ್ತು ತರಗತಿ ಹಾಗೂ ಊಟದ ನಡುವೆ ನಿಯಮಿತವಾಗಿ ಕುಡಿಯಿರಿ.',
      },
      fiber: {
        level: riskLevel(fiberRisk),
        titleEn: 'Fiber deficiency risk',
        titleKn: 'ನಾರು ಕೊರತೆ ಅಪಾಯ',
        bodyEn: category === 'overweight' || category === 'obese'
          ? 'Add vegetables, fruits, ragi, jowar, and sprouts to support fullness and gut health.'
          : 'Keep daily fruits and vegetables in the meal plan to maintain digestion and satiety.',
        bodyKn: category === 'overweight' || category === 'obese'
          ? 'ತೃಪ್ತಿ ಮತ್ತು ಜೀರ್ಣಕ್ಕೆ ನೆರವಾಗಲು ಹಣ್ಣು, ತರಕಾರಿ, ರಾಗಿ, ಜೋಳ ಮತ್ತು ಮೊಳಕೆಕಾಳು ಸೇರಿಸಿ.'
          : 'ಜೀರ್ಣ ಮತ್ತು ತೃಪ್ತಿಗಾಗಿ ಪ್ರತಿದಿನ ಹಣ್ಣು ಮತ್ತು ತರಕಾರಿ ಸೇರಿಸಿ.',
      },
    };
  }

  function buildModel({ bmi, plan }) {
    const studentName = bmi?.student_name || plan?.student_name || 'Student';
    const age = toNumber(bmi?.age ?? plan?.age ?? (plan?.age_group ? String(plan.age_group).split('-')[0] : null)) ?? 0;
    const gender = bmi?.gender || plan?.gender || '';
    const height = bmi?.height_cm ?? bmi?.height ?? null;
    const weight = bmi?.weight_kg ?? bmi?.weight ?? null;
    const bmiValue = bmi?.bmi_value ?? null;
    const bmiCategory = String(bmi?.classification || bmi?.bmi_class || plan?.bmi_class || 'normal').toLowerCase();
    const categoryMeta = CATEGORY_RULES[bmiCategory] || CATEGORY_RULES.normal;
    const water = ageLabel(age);
    const signals = buildMealSignals(plan);

    const proteinFoodList = bmiCategory === 'underweight'
      ? [
          { en: 'Milk', kn: 'ಹಾಲು' },
          { en: 'Eggs', kn: 'ಮೊಟ್ಟೆಗಳು' },
          { en: 'Paneer', kn: 'ಪನೀರ್' },
          { en: 'Dal', kn: 'ಬೇಳೆ' },
        ]
      : [
          { en: 'Dal', kn: 'ಬೇಳೆ' },
          { en: 'Milk', kn: 'ಹಾಲು' },
          { en: 'Eggs', kn: 'ಮೊಟ್ಟೆಗಳು' },
          { en: 'Groundnuts', kn: 'ಕಡಲೆಕಾಯಿ' },
        ];

    const lunchIdeas = bmiCategory === 'underweight'
      ? [
          { en: 'Ragi mudde with dal and ghee', kn: 'ರಾಗಿ ಮುದ್ದೆ, ಬೇಳೆ ಮತ್ತು ತುಪ್ಪ' },
          { en: 'Rice, egg curry, and milk', kn: 'ಅನ್ನ, ಮೊಟ್ಟೆ ಕರಿ ಮತ್ತು ಹಾಲು' },
          { en: 'Jowar roti with paneer curry', kn: 'ಜೋಳದ ರೊಟ್ಟಿ ಮತ್ತು ಪನೀರ್ ಕರಿ' },
        ]
      : bmiCategory === 'overweight' || bmiCategory === 'obese'
        ? [
            { en: 'Jowar roti, green gram curry, and salad', kn: 'ಜೋಳದ ರೊಟ್ಟಿ, ಹೆಸರುಕಾಳು ಕರಿ ಮತ್ತು ಸಲಾಡ್' },
            { en: 'Ragi dosa with sambar and curd', kn: 'ರಾಗಿ ದೋಸೆ, ಸಾಂಬಾರ್ ಮತ್ತು ಮೊಸರು' },
            { en: 'Rice with vegetables and buttermilk', kn: 'ಅನ್ನ, ತರಕಾರಿ ಮತ್ತು ಮಜ್ಜಿಗೆ' },
          ]
        : [
            { en: 'Ragi dosa with chutney and fruit', kn: 'ರಾಗಿ ದೋಸೆ, ಚಟ್ನಿ ಮತ್ತು ಹಣ್ಣು' },
            { en: 'Rice, dal, and vegetable curry', kn: 'ಅನ್ನ, ಬೇಳೆ ಮತ್ತು ತರಕಾರಿ ಕರಿ' },
            { en: 'Jowar roti with greens and curd', kn: 'ಜೋಳದ ರೊಟ್ಟಿ, ಸೊಪ್ಪು ಮತ್ತು ಮೊಸರು' },
          ];

    const activities = bmiCategory === 'underweight'
      ? '45–60 minutes of light play, stretching, and relaxed outdoor movement every day.'
      : bmiCategory === 'overweight' || bmiCategory === 'obese'
        ? '60–90 minutes of brisk walking, cycling, games, or school PT activities daily.'
        : '60 minutes of active play, sports, walking, and school movement each day.';

    return {
      studentName,
      age,
      gender: formatGender(gender),
      height: height != null ? `${height} cm` : '—',
      weight: weight != null ? `${weight} kg` : '—',
      bmiValue: bmiValue != null ? `${bmiValue} kg/m²` : '—',
      bmiCategory,
      categoryMeta,
      water,
      signals,
      risks: buildRiskProfile({ bmiCategory, age, gender, plan }),
      proteinFoodList,
      lunchIdeas,
      activities,
      weeklyGoals: WEEKLY_GOALS,
      karnatakaFoods: KARNATAKA_FOODS,
    };
  }

  function renderSummaryCard(labelEn, labelKn, value, valueKn) {
    return `
      <div class="advisor-summary-card">
        <div class="advisor-summary-label">${escapeHtml(labelEn)}</div>
        <div class="advisor-summary-value">${escapeHtml(value)}</div>
        <div class="advisor-summary-kn kn">${escapeHtml(labelKn)}${valueKn ? ` · ${escapeHtml(valueKn)}` : ''}</div>
      </div>`;
  }

  function renderActionCard(card) {
    const riskClass = card.level ? ` advisor-risk-${card.level}` : '';
    return `
      <div class="advisor-action-card${riskClass}">
        <div class="advisor-action-top">
          <div class="advisor-action-icon">${card.icon}</div>
          <div>
            <div class="advisor-action-title">${escapeHtml(card.titleEn)}</div>
            <div class="advisor-action-kn kn">${escapeHtml(card.titleKn)}</div>
          </div>
        </div>
        <div class="advisor-action-body">${escapeHtml(card.bodyEn)}</div>
        <div class="kn advisor-action-body" style="margin-top:0.35rem; color:#64748B;">${escapeHtml(card.bodyKn)}</div>
        ${card.items?.length ? `
          <div class="advisor-action-list">
            ${card.items.map((item) => `<span><strong>•</strong> <span>${escapeHtml(item.en)}<span class="kn"> · ${escapeHtml(item.kn)}</span></span></span>`).join('')}
          </div>` : ''}
      </div>`;
  }

  function renderRiskCard(risk) {
    return `
      <div class="advisor-risk-card">
        <div class="advisor-risk-top">
          <div class="advisor-risk-label">${escapeHtml(risk.titleEn)}</div>
          <div class="advisor-risk-level ${escapeHtml(risk.level)}">${escapeHtml(risk.level)}</div>
        </div>
        <div class="advisor-risk-copy">${escapeHtml(risk.bodyEn)}</div>
        <div class="kn advisor-risk-copy" style="margin-top:0.3rem; color:#64748B;">${escapeHtml(risk.bodyKn)}</div>
      </div>`;
  }

  function renderAdvisor(container, input) {
    if (!container) return;

    const model = buildModel(input);
    const hasData = Boolean(input?.bmi || input?.plan);
    if (!hasData) {
      container.classList.add('hidden');
      container.innerHTML = '';
      return;
    }

    const riskCards = Object.values(model.risks).map(renderRiskCard).join('');

    const quickActions = [
      {
        icon: '⚖️',
        titleEn: 'Healthy Weight',
        titleKn: 'ಆರೋಗ್ಯಕರ ತೂಕ',
        bodyEn: model.categoryMeta.titleEn + ' - ' + model.categoryMeta.summaryEn,
        bodyKn: model.categoryMeta.titleKn + ' - ' + model.categoryMeta.summaryKn,
      },
      {
        icon: '💧',
        titleEn: 'Water Intake',
        titleKn: 'ನೀರಿನ ಸೇವನೆ',
        bodyEn: `Recommended daily water intake for ${model.gender.en.toLowerCase() === 'not specified' ? 'this student' : model.gender.en.toLowerCase()} aged ${model.age || 'school-age'} is ${model.water.valueEn}.`,
        bodyKn: `ಈ ವಿದ್ಯಾರ್ಥಿಗೆ ಸೂಕ್ತ ದೈನಂದಿನ ನೀರಿನ ಪ್ರಮಾಣ ${model.water.valueKn}.`,
      },
      {
        icon: '💪',
        titleEn: 'Protein Foods',
        titleKn: 'ಪ್ರೋಟೀನ್ ಆಹಾರಗಳು',
        bodyEn: 'Keep protein in every meal using school-friendly options.',
        bodyKn: 'ಶಾಲೆಗೆ ಹೊಂದುವ ಆಯ್ಕೆಗಳ ಮೂಲಕ ಪ್ರತಿ ಊಟದಲ್ಲೂ ಪ್ರೋಟೀನ್ ಸೇರಿಸಿ.',
        items: model.proteinFoodList,
      },
      {
        icon: '🥘',
        titleEn: 'Karnataka Foods',
        titleKn: 'ಕರ್ನಾಟಕ ಆಹಾರಗಳು',
        bodyEn: 'Use local foods that are affordable, familiar, and easy to serve.',
        bodyKn: 'ಸ್ಥಳೀಯ, ಲಭ್ಯವಿರುವ ಮತ್ತು ಸುಲಭವಾಗಿ ನೀಡಬಹುದಾದ ಆಹಾರಗಳನ್ನು ಬಳಸಿ.',
        items: model.karnatakaFoods,
      },
      {
        icon: '🍱',
        titleEn: 'School Lunch Ideas',
        titleKn: 'ಶಾಲಾ ಮಧ್ಯಾಹ್ನ ಊಟದ ಕಲ್ಪನೆಗಳು',
        bodyEn: 'A few lunch ideas tailored to the student profile and meal plan.',
        bodyKn: 'ವಿದ್ಯಾರ್ಥಿ ಪ್ರೊಫೈಲ್ ಮತ್ತು ಯೋಜನೆಗೆ ಹೊಂದುವ ಕೆಲ ಮಧ್ಯಾಹ್ನ ಊಟದ ಕಲ್ಪನೆಗಳು.',
        items: model.lunchIdeas,
      },
      {
        icon: '🎯',
        titleEn: 'Weekly Goal',
        titleKn: 'ವಾರದ ಗುರಿ',
        bodyEn: 'Small weekly targets that keep the nutrition plan actionable.',
        bodyKn: 'ಆಹಾರ ಯೋಜನೆಯನ್ನು ಅನುಸರಿಸಲು ಸುಲಭವಾಗುವ ವಾರದ ಗುರಿಗಳು.',
        items: model.weeklyGoals,
      },
      {
        icon: '🛡️',
        titleEn: 'Nutrition Risk',
        titleKn: 'ಪೋಷಣೆಯ ಅಪಾಯ',
        bodyEn: 'Look at the current risk areas before making changes to the menu.',
        bodyKn: 'ಮೆನು ಬದಲಾಯಿಸುವ ಮೊದಲು ಪ್ರಸ್ತುತ ಅಪಾಯಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.',
      },
      {
        icon: '🏃',
        titleEn: 'Recommended Activity',
        titleKn: 'ಶಿಫಾರಸು ಮಾಡಿದ ಚಟುವಟಿಕೆ',
        bodyEn: model.activities,
        bodyKn: model.bmiCategory === 'underweight'
          ? 'ಹಗುರವಾದ ಆಟ, ಸ್ಟ್ರೆಚಿಂಗ್ ಮತ್ತು ನಿಯಮಿತ ಹೊರಾಂಗಣ ಚಟುವಟಿಕೆ.'
          : model.bmiCategory === 'overweight' || model.bmiCategory === 'obese'
            ? 'ಚುರುಕಿನ ನಡೆ, ಸೈಕ್ಲಿಂಗ್ ಮತ್ತು ಸಕ್ರಿಯ ಆಟಗಳು.'
            : 'ನಿತ್ಯದ ಚಟುವಟಿಕೆ ಮತ್ತು ಹೊರಾಂಗಣ ಆಟ.'
      },
    ];

    container.innerHTML = `
      <section class="advisor-shell">
        <div class="advisor-header">
          <div class="advisor-kicker">NutriPrint AI Advisor</div>
          <div class="mt-2 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <h2 class="advisor-title text-2xl sm:text-3xl">Rule-based nutrition guidance</h2>
              <p class="advisor-subtitle mt-2">Deterministic recommendations based on BMI, age, gender, and meal data. No chat, no AI API, no waiting.</p>
            </div>
            <div class="rounded-2xl bg-white/15 px-4 py-3 text-sm font-semibold text-white/95 backdrop-blur">
              <div>${escapeHtml(model.categoryMeta.titleEn)}</div>
              <div class="kn text-xs text-white/80">${escapeHtml(model.categoryMeta.titleKn)}</div>
            </div>
          </div>
        </div>

        <div class="advisor-body">
          <div class="advisor-summary-grid">
            ${renderSummaryCard('Student Name', 'ವಿದ್ಯಾರ್ಥಿ ಹೆಸರು', model.studentName)}
            ${renderSummaryCard('Age', 'ವಯಸ್ಸು', model.age ? `${model.age}` : '—')}
            ${renderSummaryCard('Gender', 'ಲಿಂಗ', model.gender.en, model.gender.kn)}
            ${renderSummaryCard('Height', 'ಎತ್ತರ', model.height)}
            ${renderSummaryCard('Weight', 'ತೂಕ', model.weight)}
            ${renderSummaryCard('BMI Value', 'BMI ಮೌಲ್ಯ', model.bmiValue)}
            ${renderSummaryCard('BMI Category', 'BMI ವರ್ಗ', model.bmiCategory.toUpperCase(), model.categoryMeta.titleKn)}
            ${renderSummaryCard('Water Intake', 'ನೀರಿನ ಸೇವನೆ', model.water.valueEn, model.water.labelKn)}
          </div>

          <div class="advisor-section">
            <div class="advisor-section-head">
              <div>
                <div class="advisor-section-title">Quick Actions</div>
                <div class="advisor-section-note kn">ತ್ವರಿತ ಕ್ರಮಗಳ ಕಾರ್ಡ್‌ಗಳು</div>
              </div>
              <div class="advisor-section-note">8 structured recommendations</div>
            </div>
            <div class="advisor-actions-grid">
              ${quickActions.map(renderActionCard).join('')}
            </div>
          </div>

          <div class="advisor-detail-grid">
            <div class="advisor-detail-card">
              <div class="advisor-detail-title">Personalized Recommendations</div>
              <div class="advisor-detail-kn kn">ವೈಯಕ್ತಿಕ ಶಿಫಾರಸುಗಳು</div>
              <div class="advisor-detail-copy">${escapeHtml(model.categoryMeta.summaryEn)}</div>
              <div class="kn advisor-detail-copy" style="margin-top:0.35rem; color:#64748B;">${escapeHtml(model.categoryMeta.summaryKn)}</div>

              <div class="advisor-divider"></div>

              <div class="advisor-food-list">
                ${model.categoryMeta.snackEn ? `
                  <div class="advisor-food-item">
                    <strong>Healthy snack guidance</strong>
                    <span>${escapeHtml(model.categoryMeta.snackEn)}</span>
                    <span class="kn">${escapeHtml(model.categoryMeta.snackKn)}</span>
                  </div>` : ''}
                ${model.water ? `
                  <div class="advisor-food-item">
                    <strong>Water target</strong>
                    <span>${escapeHtml(model.water.valueEn)} for ${escapeHtml(model.water.labelEn)}</span>
                    <span class="kn">${escapeHtml(model.water.valueKn)} · ${escapeHtml(model.water.labelKn)}</span>
                  </div>` : ''}
                <div class="advisor-food-item">
                  <strong>School lunch focus</strong>
                  <span>${escapeHtml(model.categoryMeta.titleEn)} meals should stay balanced and practical for school service.</span>
                  <span class="kn">${escapeHtml(model.categoryMeta.titleKn)} ಊಟಗಳು ಶಾಲೆಯ ಸೇವೆಗೆ ಅನುಕೂಲವಾಗುವಂತೆ ಸಮತೋಲನವಾಗಿರಲಿ.</span>
                </div>
              </div>
            </div>

            <div class="advisor-detail-card">
              <div class="advisor-detail-title">Nutrition Risk</div>
              <div class="advisor-detail-kn kn">ಪೋಷಣೆಯ ಅಪಾಯ</div>
              <div class="advisor-risk-grid">
                ${riskCards}
              </div>

              <div class="advisor-divider"></div>

              <div class="advisor-detail-title">Weekly Goal</div>
              <div class="advisor-detail-kn kn">ವಾರದ ಗುರಿ</div>
              <div class="advisor-goal-list">
                ${model.weeklyGoals.map((goal) => `
                  <div class="advisor-goal-item">
                    <strong>${escapeHtml(goal.en)}</strong>
                    <span class="kn">${escapeHtml(goal.kn)}</span>
                  </div>`).join('')}
              </div>
            </div>
          </div>
        </div>
      </section>`;

    container.classList.remove('hidden');
  }

  function loadStoredBMI() {
    try {
      const stored = localStorage.getItem('nutriprint_last_bmi');
      if (!stored) return null;
      const parsed = JSON.parse(stored);
      if (parsed && typeof parsed === 'object') {
        window.lastBMIResult = parsed;
      }
      return parsed;
    } catch (_) {
      return null;
    }
  }

  window.NutriPrintAdvisor = {
    render(container, input) {
      renderAdvisor(container, input);
    },
    renderBMI(container, bmi) {
      renderAdvisor(container, { bmi });
    },
    renderMeal(container, plan, bmi) {
      renderAdvisor(container, { bmi: bmi || window.lastBMIResult || loadStoredBMI(), plan });
    },
    loadStoredBMI,
  };

  window.addEventListener('DOMContentLoaded', loadStoredBMI);
})();