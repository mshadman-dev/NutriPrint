let lastBMIResult = null;

async function calculateBMI() {
  const name   = document.getElementById('bmiName').value.trim();
  const age    = document.getElementById('bmiAge').value;
  const gender = document.getElementById('bmiGender').value;
  const height = document.getElementById('bmiHeight').value;
  const weight = document.getElementById('bmiWeight').value;

  if (!name || !age || !height || !weight) {
    // Show inline validation error instead of alert
    const resultEl = document.getElementById('bmiResult');
    if (resultEl) {
      resultEl.classList.remove('hidden');
      resultEl.innerHTML = `
        <div class="es-toast es-toast--warn">
          <span class="es-toast-icon">⚠️</span>
          <div class="es-toast-body">
            <div class="es-toast-title">Missing information</div>
            <div class="es-toast-msg">Please fill in all fields — Name, Age, Height, and Weight — to calculate BMI.</div>
          </div>
        </div>`;
    }
    return;
  }

  // Show loading state
  const btn        = document.querySelector('button[onclick="calculateBMI()"]');
  const resultEl   = document.getElementById('bmiResult');
  const advisorEl  = document.getElementById('advisorPanel');

  if (btn) { btn.disabled = true; btn.textContent = 'Analyzing…'; }

  // Show a loading card where the result will appear
  if (resultEl) {
    resultEl.classList.remove('hidden');
    resultEl.innerHTML = `
      <div class="ld-bmi-card">
        <div class="ld-bmi-spinner" role="status" aria-label="Calculating BMI"></div>
        <div>
          <p class="ld-bmi-label">Analyzing student measurements…</p>
          <p class="ld-bmi-sub">Calculating BMI, percentile, and Z-score</p>
        </div>
        <div class="ld-bmi-skeleton w-full">
          <div class="ld-shimmer ld-sk-line ld-sk-line--short"></div>
          <div class="ld-shimmer ld-sk-line ld-sk-line--thick" style="margin-top:0.25rem;"></div>
          <div class="ld-shimmer ld-sk-line ld-sk-line--full" style="height:10px;margin-top:0.75rem;border-radius:9999px;"></div>
          <div class="ld-shimmer ld-sk-line ld-sk-line--med" style="margin-top:0.5rem;"></div>
        </div>
      </div>`;
    resultEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  try {
    const res = await fetch('/api/bmi/calculate', {
      method  : 'POST',
      headers : {'Content-Type':'application/json'},
      body    : JSON.stringify({
        student_name : name,
        age          : parseInt(age),
        gender,
        height_cm    : parseFloat(height),
        weight_kg    : parseFloat(weight),
        teacher_id   : localStorage.getItem('teacher_id') || null,
      })
    });

    if (!res.ok) {
      if (resultEl) {
        resultEl.classList.remove('hidden');
        resultEl.innerHTML = `
          <div class="es-card es-card--error es-card--full">
            <div class="es-icon es-icon--red">⚠️</div>
            <div class="es-title">Assessment failed</div>
            <div class="es-body">Unable to calculate BMI right now. Please check the values and try again.</div>
            <button class="es-btn" onclick="document.getElementById('bmiResult').classList.add('hidden')">Try Again</button>
          </div>`;
      }
      return;
    }

    const data = await res.json();

    lastBMIResult = data;
    window.lastBMIResult = data;
    try {
      localStorage.setItem('nutriprint_last_bmi', JSON.stringify(data));
    } catch (_) {}

    // ── Auto-save to progress tracker ──────────────────────────────────────
    try {
      const ptKey     = 'bmi_history_' + data.student_name;
      const ptRecords = JSON.parse(localStorage.getItem(ptKey) || '[]');
      ptRecords.push({
        date           : new Date().toLocaleDateString('en-IN'),
        bmi            : data.bmi_value,
        classification : data.classification,
        age            : data.age,
        gender         : data.gender,
        percentile     : data.percentile,
        z_score        : data.z_score,
        weight_kg      : parseFloat(document.getElementById('bmiWeight')?.value || 0),
        height_cm      : parseFloat(document.getElementById('bmiHeight')?.value || 0),
        label          : null,
      });
      localStorage.setItem(ptKey, JSON.stringify(ptRecords));
      // If progress tracker is on the same page, refresh it
      if (typeof window.ptRender === 'function') window.ptRender();
    } catch (_) {}

    // Restore result el HTML structure before populating
    resultEl.innerHTML = `
      <div class="flex items-start justify-between gap-4">
        <div>
          <h3 id="resultName" class="heading text-2xl font-bold text-slate-900"></h3>
          <p id="resultBMI" class="mt-1 text-sm text-slate-500"></p>
        </div>
        <span id="resultBadge" class="rounded-full px-4 py-2 text-sm font-bold"></span>
      </div>
      <div class="mt-5">
        <div id="bmiGaugeContainer"></div>
        <p id="resultPercentile" class="mt-2 text-right text-xs text-slate-500"></p>
      </div>
      <div id="resultAdviceEN" class="mt-5 rounded-2xl bg-emerald-50 p-4 text-sm text-slate-700"></div>
      <div id="resultAdviceKN" class="kn mt-3 rounded-2xl bg-amber-50 p-4 text-sm text-slate-700"></div>
      <button onclick="prefillMealForm()" class="btn-secondary mt-6 w-full py-3">Generate Meal Plan for this Student</button>`;

    showBMIResult(data);
    showGrowthChart(data.student_name);

  } catch (err) {
    console.error('BMI error:', err);

    
    if (resultEl) {
      resultEl.classList.remove('hidden');
      resultEl.innerHTML = `
        <div class="es-card es-card--error es-card--full">
          <div class="es-icon es-icon--red">🔌</div>
          <div class="es-title">Connection problem</div>
          <div class="es-body">Unable to reach the assessment service. Please check your connection and try again.</div>
          <button class="es-btn" onclick="document.getElementById('bmiResult').classList.add('hidden');document.getElementById('bmiName').focus()">Try Again</button>
        </div>`;
    }
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'Calculate BMI'; }
  }
}

function showBMIResult(data) {
  document.getElementById('bmiResult').classList.remove('hidden');

  document.getElementById('resultName').textContent =
    `${data.student_name} — ${data.age} yrs, ${data.gender}`;
  document.getElementById('resultBMI').textContent =
    `BMI: ${data.bmi_value} kg/m² · Z-score: ${data.z_score}`;

  const badge = document.getElementById('resultBadge');
  badge.textContent  = data.classification.toUpperCase();
  badge.className    = `px-4 py-1.5 rounded-full text-sm font-bold badge-${data.classification}`;

  // ── BMI Category Gauge ───────────────────────────────────────────────────
  // Zone boundaries based on IAP pediatric percentile thresholds used by
  // bmi_calculator.py:  P5 = underweight/normal, P85 = normal/overweight,
  // P95 = overweight/obese.
  //
  // Visual band allocations (fixed widths so labels align with zones):
  //   Underweight  →  0 – 12.5%   (percentile  0–5)
  //   Normal       → 12.5 – 75%   (percentile  5–85)
  //   Overweight   → 75 – 87.5%   (percentile 85–95)
  //   Obese        → 87.5 – 100%  (percentile 95–99.9)
  //
  // The marker position is derived from the classification and percentile
  // so it always lands inside the correct coloured band.

  const ZONES = [
    { key: 'underweight', label: 'Underweight', color: '#3B82F6',
      pLow:  0,  pHigh:  5,  vLow:  0,   vHigh: 12.5 },
    { key: 'normal',      label: 'Normal',      color: '#10B981',
      pLow:  5,  pHigh: 85,  vLow: 12.5, vHigh: 75   },
    { key: 'overweight',  label: 'Overweight',  color: '#F97316',
      pLow: 85,  pHigh: 95,  vLow: 75,   vHigh: 87.5 },
    { key: 'obese',       label: 'Obese',       color: '#EF4444',
      pLow: 95,  pHigh: 100, vLow: 87.5, vHigh: 100  },
  ];

  // Find the zone that matches the server-returned classification.
  const zone = ZONES.find(z => z.key === data.classification) || ZONES[1];

  // Map percentile to a visual position clamped inside the correct zone.
  const pClamped = Math.max(zone.pLow, Math.min(zone.pHigh - 0.01, data.percentile));
  const fraction = (zone.pHigh > zone.pLow)
    ? (pClamped - zone.pLow) / (zone.pHigh - zone.pLow)
    : 0.5;
  const markerPct = zone.vLow + fraction * (zone.vHigh - zone.vLow);

  // Build the gauge HTML
  const gaugeContainer = document.getElementById('bmiGaugeContainer');
  if (gaugeContainer) {
    gaugeContainer.innerHTML = `
      <div style="position:relative; margin-bottom:6px;">
        <!-- Segmented colour track -->
        <div style="display:flex; height:14px; border-radius:8px; overflow:hidden; box-shadow:inset 0 1px 3px rgba(0,0,0,.12);">
          <div style="width:12.5%; background:#93C5FD;" title="Underweight (P0–P5)"></div>
          <div style="width:62.5%; background:#6EE7B7;" title="Normal (P5–P85)"></div>
          <div style="width:12.5%; background:#FED7AA;" title="Overweight (P85–P95)"></div>
          <div style="width:12.5%; background:#FCA5A5;" title="Obese (P95+)"></div>
        </div>
        <!-- Active zone highlight overlay -->
        <div style="
          position:absolute; top:0; height:14px; border-radius:8px;
          left:${zone.vLow}%; width:${zone.vHigh - zone.vLow}%;
          background:${zone.color}; opacity:0.55; pointer-events:none;">
        </div>
        <!-- Marker dot with animated drop-in -->
        <div id="bmiMarker" style="
          position:absolute; top:50%; transform:translate(-50%, -50%);
          left:0%;
          width:20px; height:20px; border-radius:50%;
          background:${zone.color};
          border:3px solid #fff;
          box-shadow:0 2px 6px rgba(0,0,0,.30);
          transition:left 0.9s cubic-bezier(.34,1.56,.64,1);
          z-index:10;">
        </div>
      </div>
      <!-- Zone boundary labels aligned to band edges -->
      <div style="display:flex; font-size:10px; color:#64748b; margin-top:3px; user-select:none;">
        <span style="width:12.5%; text-align:left;  padding-left:2px;">Underweight</span>
        <span style="width:62.5%; text-align:center;">Normal</span>
        <span style="width:12.5%; text-align:center;">Overweight</span>
        <span style="width:12.5%; text-align:right; padding-right:2px;">Obese</span>
      </div>`;

    // Animate marker to final position after a short delay (allows CSS transition)
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        const marker = document.getElementById('bmiMarker');
        if (marker) marker.style.left = `${markerPct}%`;
      });
    });
  }

  document.getElementById('resultPercentile').textContent =
    `${data.percentile}th percentile · ${zone.label}`;
  document.getElementById('resultAdviceEN').textContent = data.advice_en;
  document.getElementById('resultAdviceKN').textContent = data.advice_kn;

  if (window.NutriPrintAdvisor) {
    const advisorPanel = document.getElementById('advisorPanel');
    window.NutriPrintAdvisor.renderBMI(advisorPanel, data);
  }

  // Scroll to result
  document.getElementById('bmiResult').scrollIntoView({behavior:'smooth', block:'center'});
}

function prefillMealForm() {
  if (!lastBMIResult) return;
  const url = new URL(window.location.origin + '/meal-planner');
  url.searchParams.set('name', lastBMIResult.student_name || '');
  url.searchParams.set('category', lastBMIResult.classification || '');
  url.searchParams.set('bmi', lastBMIResult.bmi_value || '');
  window.location.href = url.toString();
}

// Voice input
function startVoice(fieldId) {
  if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
    const resultEl = document.getElementById('bmiResult');
    if (resultEl) {
      resultEl.classList.remove('hidden');
      resultEl.innerHTML = `
        <div class="es-toast es-toast--info">
          <span class="es-toast-icon">🎙️</span>
          <div class="es-toast-body">
            <div class="es-toast-title">Voice input not supported</div>
            <div class="es-toast-msg">Your browser does not support voice input. Please type the value directly.</div>
          </div>
        </div>`;
    }
    return;
  }
  const SR   = window.SpeechRecognition || window.webkitSpeechRecognition;
  const rec  = new SR();
  rec.lang   = 'en-IN';
  rec.start();
  rec.onresult = (e) => {
    const val = e.results[0][0].transcript.replace(/[^0-9.]/g,'');
    document.getElementById(fieldId).value = val;
  };
}

async function showGrowthChart(studentName) {
  // Only shows if same student assessed before
  const records = JSON.parse(
    localStorage.getItem(`bmi_history_${studentName}`) || '[]'
  );

  // Save current result to history
  if (lastBMIResult) {
    records.push({
      date : new Date().toLocaleDateString('en-IN'),
      bmi  : lastBMIResult.bmi_value,
      class: lastBMIResult.classification,
    });
    localStorage.setItem(
      `bmi_history_${studentName}`,
      JSON.stringify(records)
    );
  }

  if (records.length < 2) return; // Need at least 2 points

  // Inject chart container
  const oldChart = document.getElementById('growthChartWrapper');
  if (oldChart) oldChart.remove();
  
  document.getElementById('bmiResult').insertAdjacentHTML(
  'beforeend',
  `<div id="growthChartWrapper" class="mt-6">
     <p class="heading font-bold text-gray-800 mb-3">
       📈 Growth Trend
       <span class="kn text-orange-400 text-sm ml-1">
         ಬೆಳವಣಿಗೆ ಗ್ರಾಫ್
       </span>
     </p>
     <canvas id="growthChart" height="120"></canvas>
   </div>`
);

  const ctx = document.getElementById('growthChart').getContext('2d');
  new Chart(ctx, {
    type : 'line',
    data : {
      labels   : records.map(r => r.date),
      datasets : [{
        label           : 'BMI',
        data            : records.map(r => r.bmi),
        borderColor     : '#1D9E75',
        backgroundColor : 'rgba(29,158,117,0.1)',
        borderWidth     : 3,
        pointRadius     : 6,
        pointBackgroundColor: records.map(r =>
          r.class === 'normal'      ? '#10B981' :
          r.class === 'underweight' ? '#3B82F6' :
          r.class === 'overweight'  ? '#F97316' : '#EF4444'
        ),
        tension: 0.4,
        fill   : true,
      }]
    },
    options: {
      responsive : true,
      plugins    : {
        legend : { display: false },
        tooltip: {
          callbacks: {
            label: ctx =>
              `BMI: ${ctx.raw} — ${records[ctx.dataIndex].class}`
          }
        }
      },
      scales: {
        y: {
          min  : 10,
          max  : 30,
          title: { display:true, text:'BMI (kg/m²)' }
        }
      }
    }
  });
}



// Restore prefill from dashboard reassess on page load
window.addEventListener('DOMContentLoaded', () => {

  const prefillName   = localStorage.getItem('prefill_name');
  const prefillAge    = localStorage.getItem('prefill_age');
  const prefillGender = localStorage.getItem('prefill_gender');

  if (prefillName) {
    const bmiName     = document.getElementById('bmiName');
    const bmiAge      = document.getElementById('bmiAge');
    const bmiGender   = document.getElementById('bmiGender');
    const mealStudent = document.getElementById('mealStudent');
    if (bmiName)   bmiName.value   = prefillName;
    if (bmiAge && prefillAge)   bmiAge.value   = prefillAge;
    if (bmiGender && prefillGender) bmiGender.value = prefillGender;
    if (mealStudent) mealStudent.value = prefillName;
    localStorage.removeItem('prefill_name');
    localStorage.removeItem('prefill_age');
    localStorage.removeItem('prefill_gender');
  }

  try {
    const storedBmi = localStorage.getItem('nutriprint_last_bmi');
    if (storedBmi && !window.lastBMIResult) {
      window.lastBMIResult = JSON.parse(storedBmi);
      lastBMIResult = window.lastBMIResult;
    }
  } catch (_) {}
});
