// PrepCoach frontend. Two paths, one UI:
//  - API mode: talks to the Flask backend (/api/*), live or stub provider.
//  - Demo mode: if the API is unreachable (e.g. the static GitHub Pages
//    copy), the same three flows run in-browser from demo-data.json and
//    are labelled demo mode throughout. No fake "live" claims.
(function () {
  'use strict';
  var DEMO = false, demoData = null, session = null, dsaProblems = [];

  function el(id) { return document.getElementById(id); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

  function setBanner(text, live) {
    var b = el('mode-banner'); b.textContent = text;
    b.className = 'banner' + (live ? ' live' : '');
  }

  function api(path, opts) {
    return fetch(path, opts).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    });
  }

  // ---------- tabs ----------
  document.querySelectorAll('nav button').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('nav button').forEach(function (b) { b.classList.remove('active'); });
      document.querySelectorAll('.tab').forEach(function (t) { t.classList.remove('active'); });
      btn.classList.add('active');
      el('tab-' + btn.dataset.tab).classList.add('active');
    });
  });

  // ---------- interview ----------
  function demoStartInterview() {
    var role = el('iv-role').value, level = el('iv-level').value;
    var bank = demoData.interview[role][level].slice();
    session = { bank: bank, idx: 0, answers: [], followup: false, question: null };
    el('iv-area').classList.remove('hidden');
    el('iv-debrief').classList.add('hidden');
    demoNextQuestion();
  }
  function demoNextQuestion() {
    if (session.followup) {
      session.followup = false;
      session.lastWasFollowup = true;
      session.question = "You kept that one brief — can you go deeper on '" + session.answers[session.answers.length - 1][0] + "'? Give a concrete example.";
    } else if (session.idx < session.bank.length) {
      session.question = session.bank[session.idx++];
      session.lastWasFollowup = false;
    } else {
      demoDebrief(); return;
    }
    el('iv-question').textContent = session.question;
    el('iv-answer').value = '';
  }
  function demoDebrief() {
    var strengths = [], gaps = [];
    session.answers.forEach(function (qa) {
      var topic = qa[0].split('?')[0].slice(0, 60);
      if (qa[1].split(/\s+/).length >= 20) strengths.push(topic); else gaps.push(topic);
    });
    if (!strengths.length) strengths = ['You completed the session — that itself is practice most candidates skip.'];
    if (!gaps.length) gaps = ['No thin answers; next time, push for harder follow-ups.'];
    el('iv-question').textContent = 'Interview complete — debrief below (practice guidance only).';
    var d = el('iv-debrief');
    d.textContent = 'Strengths: ' + strengths.join('; ') + '.\nGaps: ' + gaps.join('; ') + '.\nPractise next: revisit the gap topics above and rehearse one concrete example per topic.';
    d.classList.remove('hidden');
  }
  el('iv-start').addEventListener('click', function () {
    if (DEMO) { demoStartInterview(); return; }
    api('/api/interview/start', { method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ role: el('iv-role').value, level: el('iv-level').value }) })
      .then(function (d) {
        session = { id: d.session_id };
        el('iv-area').classList.remove('hidden');
        el('iv-debrief').classList.add('hidden');
        el('iv-question').textContent = d.question;
        el('iv-answer').value = '';
      }).catch(function (e) { alert('Could not start interview: ' + e.message); });
  });
  el('iv-send').addEventListener('click', function () {
    var ans = el('iv-answer').value;
    if (DEMO) {
      session.answers.push([session.question, ans]);
      if (ans.split(/\s+/).length < 20 && !session.lastWasFollowup) session.followup = true;
      demoNextQuestion(); return;
    }
    api('/api/interview/answer', { method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ session_id: session.id, answer: ans }) })
      .then(function (d) {
        if (d.finished) {
          el('iv-question').textContent = 'Interview complete — debrief below (practice guidance only).';
          var dv = el('iv-debrief');
          dv.textContent = d.debrief.guidance; dv.classList.remove('hidden');
        } else { el('iv-question').textContent = d.question; el('iv-answer').value = ''; }
      }).catch(function (e) { alert('Could not send answer: ' + e.message); });
  });

  // ---------- resume ----------
  function demoResume(text) {
    var lines = text.split('\n');
    var bullets = lines.filter(function (l) { return /^\s*(-|\*|•|\d+[.)])/.test(l); });
    var verbs = ['built','shipped','designed','led','improved','reduced','increased','automated','launched','delivered','created','developed','scaled','fixed','owned'];
    var withVerb = bullets.filter(function (b) { var l = b.toLowerCase(); return verbs.some(function (v) { return l.indexOf(v) !== -1; }); });
    var withNum = bullets.filter(function (b) { return /\d/.test(b); });
    var low = text.toLowerCase();
    var findings = [];
    findings.push({ c: 'Contact info', s: (/@/.test(text) && /\+?\d[\d\s-]{7,}/.test(text)) ? 'pass' : 'attention', e: 'Email/phone presence checked.', g: 'Add any missing contact detail at the top.' });
    ['experience','education','skills','projects'].forEach(function (sec) {
      findings.push({ c: sec[0].toUpperCase() + sec.slice(1) + ' section', s: low.indexOf(sec) !== -1 ? 'pass' : 'attention', e: low.indexOf(sec) !== -1 ? 'Section detected.' : 'No section detected.', g: 'Add the section if it is missing.' });
    });
    findings.push({ c: 'Impact wording', s: bullets.length && withVerb.length >= bullets.length / 2 ? 'pass' : 'attention', e: withVerb.length + ' of ' + bullets.length + ' bullets contain an action verb.', g: 'Start each bullet with a verb and name what changed.' });
    findings.push({ c: 'Quantified outcomes', s: withNum.length ? 'pass' : 'attention', e: withNum.length + ' bullet(s) include a number.', g: 'Add real figures only where true — never invent one.' });
    return { findings: findings, suggestions: ['Rewrite weak bullets as: <Action verb> <what you changed>, improving <metric> by <number>% — fill with real facts only.'] };
  }
  el('rs-go').addEventListener('click', function () {
    var text = el('rs-text').value;
    function render(d) {
      el('rs-out').innerHTML = d.findings.map(function (f) {
        return '<div class="finding ' + esc(f.s) + '"><strong>' + esc(f.c) + ' — ' + esc(f.s) + '</strong><br>' + esc(f.e) + '<br><em>' + esc(f.g) + '</em></div>';
      }).join('') + '<p><strong>Suggestions:</strong> ' + d.suggestions.map(esc).join('<br>') + '</p><p><em>Analysis of the text you pasted only. Nothing here was invented about your background.</em></p>';
    }
    if (DEMO) { render(demoResume(text)); return; }
    api('/api/resume', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ resume_text: text }) })
      .then(function (d) {
        render({ findings: d.findings.map(function (f) { return { c: f.criterion, s: f.status, e: f.evidence, g: f.suggestion }; }), suggestions: d.suggestions });
      }).catch(function (e) { alert('Could not analyse resume: ' + e.message); });
  });

  // ---------- DSA ----------
  function renderProblem(p) {
    el('dsa-detail').innerHTML = '<h3>' + esc(p.title) + ' <small>(' + esc(p.topic) + ' · ' + esc(p.difficulty) + ')</small></h3><p>' + esc(p.statement) + '</p>' +
      '<p><strong>Examples:</strong> ' + p.examples.map(function (ex) { return esc(ex.input) + ' → ' + esc(ex.output); }).join('; ') + '</p>' +
      '<p><strong>Edge cases to handle:</strong> ' + p.edge_cases.map(esc).join(', ') + '</p>' +
      '<pre>' + esc(p.starter) + '</pre>';
    el('dsa-code').value = p.starter;
    el('dsa-hint-text').textContent = '';
  }
  function loadProblems(topic) {
    if (DEMO) {
      dsaProblems = demoData.dsa.filter(function (p) { return !topic || p.topic === topic; });
      fillProblemSelect(); return;
    }
    api('/api/dsa/problems' + (topic ? '?topic=' + encodeURIComponent(topic) : ''))
      .then(function (d) { dsaProblems = d.problems; fillProblemSelect(); })
      .catch(function (e) { alert('Could not load problems: ' + e.message); });
  }
  function fillProblemSelect() {
    var sel = el('dsa-problem');
    sel.innerHTML = dsaProblems.map(function (p) { return '<option value="' + esc(p.id) + '">' + esc(p.title) + '</option>'; }).join('');
    if (dsaProblems.length) renderProblem(dsaProblems[0]);
    sel.onchange = function () {
      var p = dsaProblems.filter(function (x) { return x.id === sel.value; })[0];
      if (p) renderProblem(p);
    };
  }
  el('dsa-topic').addEventListener('change', function () { loadProblems(el('dsa-topic').value); });
  document.querySelectorAll('#dsa-hints button').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var pid = el('dsa-problem').value, level = parseInt(btn.dataset.level, 10);
      if (DEMO) {
        var p = demoData.dsa.filter(function (x) { return x.id === pid; })[0];
        el('dsa-hint-text').textContent = 'Hint ' + level + (level === 3 ? ' (pseudocode only)' : '') + ': ' + p.hints[level - 1];
        return;
      }
      api('/api/dsa/hint', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ problem_id: pid, level: level }) })
        .then(function (d) { el('dsa-hint-text').textContent = 'Hint ' + d.level + (d.is_pseudocode ? ' (pseudocode only)' : '') + ': ' + d.text; })
        .catch(function (e) { alert('Could not load hint: ' + e.message); });
    });
  });
  el('dsa-review').addEventListener('click', function () {
    var pid = el('dsa-problem').value, code = el('dsa-code').value;
    function render(d) {
      el('dsa-review-out').innerHTML = '<p><strong>' + esc(d.problem) + '</strong></p><p>' + esc(d.commentary) + '</p>' +
        '<p><strong>Edge checklist:</strong> ' + d.edge_checklist.map(function (e) { return esc(e.edge_case) + ': ' + (e.mentioned_in_solution ? 'mentioned' : 'not mentioned'); }).join('; ') + '</p>' +
        '<p><em>' + esc(d.note) + '</em></p>';
    }
    if (DEMO) {
      var p = demoData.dsa.filter(function (x) { return x.id === pid; })[0];
      var low = code.toLowerCase();
      render({ problem: p.title, commentary: 'Practice review: walk your solution through each stated test case by hand. Keywords spotted: ' + (p.keywords.filter(function (k) { return low.indexOf(k) !== -1; }).join(', ') || 'none') + '.',
        edge_checklist: p.edge_cases.map(function (e) { return { edge_case: e, mentioned_in_solution: e.split(' ').some(function (w) { return w.length > 3 && low.indexOf(w) !== -1; }) }; }),
        note: 'Practice review only — your code was not executed and this is not a grade.' });
      return;
    }
    api('/api/dsa/review', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ problem_id: pid, code: code }) })
      .then(render).catch(function (e) { alert('Could not review solution: ' + e.message); });
  });

  // ---------- boot ----------
  api('/api/mode').then(function (m) {
    if (m.provider === 'bharatcode') setBanner('Live mode — coaching powered by BharatCode\u2019s model API.', true);
    else setBanner('Demo mode — running on the built-in practice coach. Set BHARATCODE_API_KEY on the server for live coaching.', false);
    return api('/api/interview/roles');
  }).then(function (d) {
    el('iv-role').innerHTML = d.roles.map(function (r) { return '<option>' + esc(r) + '</option>'; }).join('');
    return api('/api/dsa/problems');
  }).then(function (d) {
    el('dsa-topic').innerHTML = '<option value="">All topics</option>' + d.topics.map(function (t) { return '<option>' + esc(t) + '</option>'; }).join('');
    dsaProblems = d.problems; fillProblemSelect();
  }).catch(function () {
    DEMO = true;
    setBanner('Demo mode — static demo copy (no backend reachable). The same three flows run in-browser from the practice bank. Set BHARATCODE_API_KEY on the server for live coaching.', false);
    fetch('demo-data.json').then(function (r) { return r.json(); }).then(function (d) {
      demoData = d;
      el('iv-role').innerHTML = Object.keys(d.interview).map(function (r) { return '<option>' + esc(r) + '</option>'; }).join('');
      el('dsa-topic').innerHTML = '<option value="">All topics</option>' + d.topics.map(function (t) { return '<option>' + esc(t) + '</option>'; }).join('');
      dsaProblems = d.dsa; fillProblemSelect();
    }).catch(function () { setBanner('Demo data failed to load. Run the Flask backend locally instead (see README).', false); });
  });
})();
