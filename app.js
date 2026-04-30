import { assessments } from './data.js';

// ==================== 应用状态 ====================
const state = {
  currentPage: 'home',
  currentAssessment: null,
  currentQuestion: 0,
  answers: {},
  quizState: 'idle' // idle | active | completed
};

// ==================== 工具函数 ====================

/** 反向计分：1↔5, 2↔4, 3→3 */
function reverseScore(value) {
  return 6 - value;
}

/**
 * 计算测评得分
 * @param {string} assessmentId
 * @param {object} answers - { questionId: score }
 * @returns {object} 依测评类型不同返回不同结构
 */
function calculateScore(assessmentId, answers) {
  const assessment = assessments.find(a => a.id === assessmentId);
  if (!assessment) return null;

  const { scoring } = assessment;

  // 计算每个维度的原始分
  const dimensionScores = {};
  scoring.dimensions.forEach(dim => {
    let sum = 0;
    dim.questionIds.forEach(qId => {
      const question = assessment.questions.find(q => q.id === qId);
      let score = answers[qId] || 0;
      if (question && question.reverse) {
        score = reverseScore(score);
      }
      sum += score;
    });

    if (assessmentId === 'attachment') {
      // 依附类型：维度分 = 10题之和 ÷ 10
      dimensionScores[dim.dimensionId] = parseFloat((sum / dim.questionIds.length).toFixed(1));
    } else {
      dimensionScores[dim.dimensionId] = sum;
    }
  });

  // 计算子维度（依附类型专用）
  let subDimensionScores = {};
  if (scoring.subDimensions) {
    scoring.subDimensions.forEach(sub => {
      let sum = 0;
      sub.questionIds.forEach(qId => {
        const question = assessment.questions.find(q => q.id === qId);
        let score = answers[qId] || 0;
        if (question && question.reverse) {
          score = reverseScore(score);
        }
        sum += score;
      });
      subDimensionScores[sub.id] = parseFloat((sum / sub.questionIds.length).toFixed(1));
    });
  }

  // 总分
  let totalScore = 0;
  if (assessmentId === 'resilience') {
    totalScore = Object.values(dimensionScores).reduce((s, v) => s + v, 0);
  }

  return {
    dimensionScores,
    subDimensionScores,
    totalScore
  };
}

/**
 * 获取等级/类型
 * @param {string} assessmentId
 * @param {object} scores - calculateScore 的返回值
 * @returns {object}
 */
function getLevel(assessmentId, scores) {
  const assessment = assessments.find(a => a.id === assessmentId);
  if (!assessment) return null;

  const { scoring } = assessment;

  if (assessmentId === 'resilience') {
    const level = scoring.levels.find(l => scores.totalScore >= l.min && scores.totalScore <= l.max);
    return { type: 'level', level, totalScore: scores.totalScore };
  }

  if (assessmentId === 'anxiety') {
    const dimEntries = scoring.dimensions.map(dim => ({
      dimensionId: dim.dimensionId,
      score: scores.dimensionScores[dim.dimensionId]
    }));
    dimEntries.sort((a, b) => b.score - a.score);

    const maxScore = dimEntries[0].score;
    const minScore = dimEntries[dimEntries.length - 1].score;

    // 均衡型判定
    if (maxScore - minScore <= 3) {
      return {
        type: 'anxiety',
        subtype: 'balanced',
        primary: null,
        secondary: null,
        label: '均衡型',
        dimensionScores: scores.dimensionScores,
        sortedDimensions: dimEntries
      };
    }

    // 双高型判定
    if (dimEntries[0].score === dimEntries[1].score) {
      return {
        type: 'anxiety',
        subtype: 'dualHigh',
        primary: dimEntries[0],
        secondary: dimEntries[1],
        label: '双高型',
        dimensionScores: scores.dimensionScores,
        sortedDimensions: dimEntries
      };
    }

    // 常规判定
    const primaryType = scoring.types.find(t => t.id === dimEntries[0].dimensionId);
    const secondaryType = scoring.types.find(t => t.id === dimEntries[1].dimensionId);
    return {
      type: 'anxiety',
      subtype: 'normal',
      primary: { ...dimEntries[0], typeInfo: primaryType },
      secondary: { ...dimEntries[1], typeInfo: secondaryType },
      label: primaryType.name,
      dimensionScores: scores.dimensionScores,
      sortedDimensions: dimEntries
    };
  }

  if (assessmentId === 'attachment') {
    const { attachmentRules } = scoring;
    const aScore = scores.dimensionScores[attachmentRules.anxietyDimensionId];
    const vScore = scores.dimensionScores[attachmentRules.avoidanceDimensionId];
    const midpoint = attachmentRules.midpoint;

    const aHigh = aScore > midpoint;
    const vHigh = vScore > midpoint;

    let rule;
    if (!aHigh && !vHigh) rule = attachmentRules.rules.find(r => r.typeId === 'secure');
    else if (aHigh && !vHigh) rule = attachmentRules.rules.find(r => r.typeId === 'anxious');
    else if (!aHigh && vHigh) rule = attachmentRules.rules.find(r => r.typeId === 'avoidant');
    else rule = attachmentRules.rules.find(r => r.typeId === 'fearful');

    return {
      type: 'attachment',
      attachmentType: rule,
      anxietyScore: aScore,
      avoidanceScore: vScore,
      subDimensionScores: scores.subDimensionScores
    };
  }

  return null;
}

// ==================== 页面渲染函数 ====================

const LIKERT_OPTIONS = [
  { value: 1, label: '完全不符合' },
  { value: 2, label: '不太符合' },
  { value: 3, label: '一般' },
  { value: 4, label: '比较符合' },
  { value: 5, label: '非常符合' }
];

/** 渲染首页 */
function renderHome() {
  const cards = assessments.map(a => `
    <div class="assessment-card" data-action="select-assessment" data-id="${a.id}">
      <div class="card-icon">${a.icon}</div>
      <div class="card-body">
        <h3 class="card-title">${a.name}</h3>
        <p class="card-subtitle">${a.subtitle}</p>
        <div class="card-tags">
          ${a.tags.map(t => `<span class="tag">${t}</span>`).join('')}
        </div>
        <div class="card-footer">
          <span class="card-price">&yen;${a.price}</span>
          <button class="btn btn-primary" data-action="select-assessment" data-id="${a.id}">开始测评</button>
        </div>
      </div>
    </div>
  `).join('');

  return `
    <div class="page page-home fade-in">
      <header class="home-header">
        <h1 class="brand-title">心知&middot;心理测评</h1>
        <p class="brand-subtitle">了解自己，是一切改变的开始</p>
      </header>
      <div class="assessment-grid">
        ${cards}
      </div>
      <footer class="home-footer">
        <p>本平台测评仅供参考，不构成专业心理诊断</p>
      </footer>
    </div>
  `;
}

/** 渲染测评介绍页 */
function renderAssessmentInfo(assessmentId) {
  const a = assessments.find(a => a.id === assessmentId);
  if (!a) return '<p>测评不存在</p>';

  const dimensionRows = a.dimensions.map(d => `
    <tr>
      <td class="dim-name">${d.name}</td>
      <td class="dim-desc">${d.description}</td>
    </tr>
  `).join('');

  return `
    <div class="page page-assessment-info fade-in">
      <nav class="back-nav">
        <button class="btn-back" data-action="go-home">&larr; 返回首页</button>
      </nav>
      <div class="info-header">
        <span class="info-icon">${a.icon}</span>
        <h2 class="info-title">${a.name}</h2>
        <p class="info-subtitle">${a.subtitle}</p>
      </div>
      <div class="info-meta">
        <span class="meta-item">&uuml; ${a.duration}</span>
        <span class="meta-item">&otilde; ${a.questionCount}题</span>
        <span class="meta-item">&yen; ${a.price}</span>
      </div>
      <p class="info-description">${a.description}</p>
      <div class="info-theory">
        <p class="theory-label">理论依据</p>
        <p>${a.theoryBasis}</p>
      </div>
      <table class="dimension-table">
        <thead>
          <tr><th>维度</th><th>说明</th></tr>
        </thead>
        <tbody>${dimensionRows}</tbody>
      </table>
      <div class="info-intro">
        <p class="intro-label">引导语</p>
        <p>${a.intro}</p>
      </div>
      <div class="info-audience">
        <p class="audience-label">适合人群</p>
        <p>${a.targetAudience}</p>
      </div>
      <button class="btn btn-primary btn-start" data-action="start-quiz" data-id="${a.id}">开始测评</button>
    </div>
  `;
}

/** 渲染答题页 */
function renderQuiz(assessmentId) {
  const a = assessments.find(a => a.id === assessmentId);
  if (!a) return '<p>测评不存在</p>';

  const qIndex = state.currentQuestion;
  const question = a.questions[qIndex];
  const total = a.questions.length;
  const progress = ((qIndex) / total) * 100;
  const currentAnswer = state.answers[question.id];
  const isLast = qIndex === total - 1;
  const isFirst = qIndex === 0;

  const options = LIKERT_OPTIONS.map(opt => `
    <button
      class="option-btn ${currentAnswer === opt.value ? 'selected' : ''}"
      data-action="answer"
      data-qid="${question.id}"
      data-value="${opt.value}"
    >
      <span class="option-value">${opt.value}</span>
      <span class="option-label">${opt.label}</span>
    </button>
  `).join('');

  return `
    <div class="page page-quiz fade-in">
      <nav class="quiz-nav-top">
        <button class="btn-back" data-action="go-assessment-info" data-id="${assessmentId}">&larr; 退出</button>
        <span class="quiz-progress-text">${qIndex + 1} / ${total}</span>
      </nav>
      <div class="progress-bar-container">
        <div class="progress-bar-fill" style="width: ${progress}%"></div>
      </div>
      <div class="question-container">
        <p class="question-text">${question.text}</p>
        <div class="options-grid">
          ${options}
        </div>
      </div>
      <div class="quiz-actions">
        <button class="btn btn-secondary" data-action="prev-question" ${isFirst ? 'disabled' : ''}>
          上一题
        </button>
        ${isLast
          ? `<button class="btn btn-primary" data-action="view-result" data-id="${assessmentId}" ${!currentAnswer ? 'disabled' : ''}>
              查看结果
            </button>`
          : `<button class="btn btn-primary" data-action="next-question" ${!currentAnswer ? 'disabled' : ''}>
              下一题
            </button>`
        }
      </div>
    </div>
  `;
}

/** 生成CSS条形图HTML */
function renderBarChart(dimensionData, maxScore) {
  return dimensionData.map(d => `
    <div class="bar-row">
      <span class="bar-label">${d.name}</span>
      <div class="bar-track">
        <div class="bar-fill ${d.colorClass || ''}" style="width: ${(d.score / maxScore) * 100}%; background-color: ${d.color || ''}"></div>
      </div>
      <span class="bar-score">${d.score}</span>
    </div>
  `).join('');
}

/** 渲染结果页 */
function renderResult(assessmentId, answers) {
  const a = assessments.find(a => a.id === assessmentId);
  if (!a) return '<p>测评不存在</p>';

  const scores = calculateScore(assessmentId, answers);
  const levelInfo = getLevel(assessmentId, scores);

  if (assessmentId === 'resilience') {
    return renderResilienceResult(a, scores, levelInfo);
  } else if (assessmentId === 'anxiety') {
    return renderAnxietyResult(a, scores, levelInfo);
  } else if (assessmentId === 'attachment') {
    return renderAttachmentResult(a, scores, levelInfo);
  }

  return '<p>未知测评类型</p>';
}

/** 职场心理韧性结果 */
function renderResilienceResult(assessment, scores, levelInfo) {
  const { level, totalScore } = levelInfo;
  const dimData = assessment.scoring.dimensions.map(dim => {
    const dimInfo = assessment.dimensions.find(d => d.id === dim.dimensionId);
    return {
      name: dimInfo.name,
      score: scores.dimensionScores[dim.dimensionId],
      maxScore: dim.maxScore
    };
  });

  const strongest = dimData.reduce((a, b) => a.score > b.score ? a : b);
  const weakest = dimData.reduce((a, b) => a.score < b.score ? a : b);

  const barChart = dimData.map(d => `
    <div class="bar-row">
      <span class="bar-label">${d.name}</span>
      <div class="bar-track">
        <div class="bar-fill" style="width: ${(d.score / d.maxScore) * 100}%; background-color: ${level.color}"></div>
      </div>
      <span class="bar-score">${d.score}/${d.maxScore}</span>
    </div>
  `).join('');

  return `
    <div class="page page-result fade-in">
      <div class="result-header">
        <div class="level-badge" style="background-color: ${level.color}">${level.id}</div>
        <h2 class="result-level-name">${level.name}</h2>
        <p class="result-summary">你的职场心理韧性总分为${totalScore}分，等级为${level.name}（${level.id}）。</p>
      </div>
      <div class="result-chart">
        <h3>维度得分</h3>
        ${barChart}
      </div>
      <div class="result-highlights">
        <div class="highlight-item highlight-strong">
          <span class="highlight-icon">&#9733;</span>
          <p>你最亮眼的维度是<strong>${strongest.name}</strong>，得分${strongest.score}分，说明你在这方面已经有了不错的基础。</p>
        </div>
        <div class="highlight-item highlight-weak">
          <span class="highlight-icon">&#9888;</span>
          <p>你最需要关注的维度是<strong>${weakest.name}</strong>，得分${weakest.score}分，这可能是你韧性体系中最需要补强的一环。</p>
        </div>
      </div>
      <div class="paid-unlock">
        <div class="unlock-icon">&#128274;</div>
        <p class="unlock-title">解锁深度报告</p>
        <p class="unlock-desc">获取维度深度解读、生活场景、改善行动方案、心理学小知识和咨询师寄语</p>
        <button class="btn btn-paid" data-action="unlock-paid-report" data-id="resilience">
          解锁完整报告 &yen;${assessment.price}
        </button>
      </div>
      <div class="result-actions">
        <button class="btn btn-secondary" data-action="go-home">返回首页</button>
        <button class="btn btn-outline" data-action="retake" data-id="resilience">重新测评</button>
      </div>
    </div>
  `;
}

/** 焦虑类型结果 */
function renderAnxietyResult(assessment, scores, levelInfo) {
  const { sortedDimensions, subtype, primary, secondary, label } = levelInfo;
  const dimData = assessment.scoring.dimensions.map(dim => {
    const dimInfo = assessment.dimensions.find(d => d.id === dim.dimensionId);
    const typeInfo = assessment.scoring.types.find(t => t.id === dim.dimensionId);
    return {
      name: dimInfo.name,
      score: scores.dimensionScores[dim.dimensionId],
      maxScore: dim.maxScore,
      color: typeInfo ? getTypeColor(dim.dimensionId) : '#95A5A6'
    };
  });

  const barChart = dimData.map(d => `
    <div class="bar-row">
      <span class="bar-label">${d.name}</span>
      <div class="bar-track">
        <div class="bar-fill" style="width: ${(d.score / d.maxScore) * 100}%; background-color: ${d.color}"></div>
      </div>
      <span class="bar-score">${d.score}/${d.maxScore}</span>
    </div>
  `).join('');

  let primarySection = '';
  if (subtype === 'balanced') {
    primarySection = `
      <div class="result-type-label balanced">
        <h2 class="result-type-name">均衡型</h2>
        <p class="result-type-tagline">你的焦虑在多个维度分布较为均衡</p>
      </div>
    `;
  } else if (subtype === 'dualHigh') {
    primarySection = `
      <div class="result-type-label dual-high">
        <h2 class="result-type-name">双高型</h2>
        <p class="result-type-tagline">你有两个焦虑维度并列最高，需要同时关注</p>
      </div>
    `;
  } else {
    const pType = primary.typeInfo;
    primarySection = `
      <div class="result-type-label" style="border-color: ${getTypeColor(pType.id)}">
        <h2 class="result-type-name">${pType.name}</h2>
        <p class="result-type-tagline">${pType.tagline}</p>
        <p class="result-type-desc">${pType.description}</p>
      </div>
      <div class="secondary-type">
        <span class="secondary-label">次要焦虑类型：</span>
        <span class="secondary-name">${secondary.typeInfo.name}</span>
      </div>
    `;
  }

  return `
    <div class="page page-result fade-in">
      <div class="result-header">
        ${primarySection}
      </div>
      <div class="result-chart">
        <h3>维度得分</h3>
        ${barChart}
      </div>
      <div class="paid-unlock">
        <div class="unlock-icon">&#128274;</div>
        <p class="unlock-title">解锁深度报告</p>
        <p class="unlock-desc">获取焦虑类型深度解读、生活场景、积极面分析、改善行动方案</p>
        <button class="btn btn-paid" data-action="unlock-paid-report" data-id="anxiety">
          解锁完整报告 &yen;${assessment.price}
        </button>
      </div>
      <div class="result-actions">
        <button class="btn btn-secondary" data-action="go-home">返回首页</button>
        <button class="btn btn-outline" data-action="retake" data-id="anxiety">重新测评</button>
      </div>
    </div>
  `;
}

/** 依附类型结果 */
function renderAttachmentResult(assessment, scores, levelInfo) {
  const { attachmentType, anxietyScore, avoidanceScore, subDimensionScores } = levelInfo;
  const subDims = assessment.scoring.subDimensions;

  const subDimData = subDims.map(sub => ({
    name: sub.name,
    score: subDimensionScores[sub.id],
    maxScore: 5.0
  }));

  const barChart = subDimData.map(d => `
    <div class="bar-row">
      <span class="bar-label">${d.name}</span>
      <div class="bar-track">
        <div class="bar-fill" style="width: ${(d.score / d.maxScore) * 100}%; background-color: ${attachmentType.color}"></div>
      </div>
      <span class="bar-score">${d.score}</span>
    </div>
  `).join('');

  return `
    <div class="page page-result fade-in">
      <div class="result-header">
        <div class="result-type-label" style="border-color: ${attachmentType.color}">
          <h2 class="result-type-name" style="color: ${attachmentType.color}">${attachmentType.name}</h2>
          <p class="result-type-tagline">${attachmentType.tagline}</p>
        </div>
        <div class="dimension-scores-row">
          <div class="dimension-score-card">
            <span class="dim-score-label">焦虑维度</span>
            <span class="dim-score-value">${anxietyScore}</span>
            <div class="dim-score-bar">
              <div class="dim-score-fill" style="width: ${(anxietyScore / 5.0) * 100}%; background-color: #E74C3C"></div>
            </div>
          </div>
          <div class="dimension-score-card">
            <span class="dim-score-label">回避维度</span>
            <span class="dim-score-value">${avoidanceScore}</span>
            <div class="dim-score-bar">
              <div class="dim-score-fill" style="width: ${(avoidanceScore / 5.0) * 100}%; background-color: #3498DB"></div>
            </div>
          </div>
        </div>
      </div>
      <div class="result-chart">
        <h3>子维度得分</h3>
        ${barChart}
      </div>
      <div class="paid-unlock">
        <div class="unlock-icon">&#128274;</div>
        <p class="unlock-title">解锁双人深度报告</p>
        <p class="unlock-desc">获取你的依附类型深度解读、关系模式、最佳伴侣匹配、关系陷阱、改善行动方案</p>
        <button class="btn btn-paid" data-action="unlock-paid-report" data-id="attachment">
          解锁完整报告 &yen;${assessment.price}
        </button>
      </div>
      <div class="share-section">
        <button class="btn btn-share" data-action="share" data-id="attachment">分享给TA</button>
        <p class="share-hint">邀请TA也来测一测，看看你们的依附类型是否互补</p>
      </div>
      <div class="result-actions">
        <button class="btn btn-secondary" data-action="go-home">返回首页</button>
        <button class="btn btn-outline" data-action="retake" data-id="attachment">重新测评</button>
      </div>
    </div>
  `;
}

/** 焦虑类型颜色映射 */
function getTypeColor(dimensionId) {
  const colorMap = {
    health: '#E74C3C',
    appearance: '#9B59B6',
    relationship: '#F39C12',
    direction: '#3498DB'
  };
  return colorMap[dimensionId] || '#95A5A6';
}

/** 渲染付费报告页 */
function renderPaidReport(assessmentId, answers) {
  const a = assessments.find(a => a.id === assessmentId);
  if (!a) return '<p>测评不存在</p>';

  const scores = calculateScore(assessmentId, answers);
  const levelInfo = getLevel(assessmentId, scores);

  if (assessmentId === 'resilience') {
    return renderResiliencePaidReport(a, scores, levelInfo);
  } else if (assessmentId === 'anxiety') {
    return renderAnxietyPaidReport(a, scores, levelInfo);
  } else if (assessmentId === 'attachment') {
    return renderAttachmentPaidReport(a, scores, levelInfo);
  }

  return '<p>未知测评类型</p>';
}

/** 职场心理韧性付费报告 */
function renderResiliencePaidReport(assessment, scores, levelInfo) {
  const { level } = levelInfo;
  const report = assessment.paidReports[level.id];
  const sections = splitPipeSections(report.dimensionAnalysis);

  const dimensionAnalysisHTML = assessment.dimensions.map((dim, i) => `
    <div class="report-section-item">
      <h4>${dim.name}</h4>
      <p>${sections[i] || ''}</p>
      <p class="theory-note">${dim.theoryNote}</p>
    </div>
  `).join('');

  const lifeScenes = splitPipeSections(report.lifeScenes);
  const actions = splitPipeSections(report.actions);

  return `
    <div class="page page-paid-report fade-in">
      <nav class="back-nav">
        <button class="btn-back" data-action="go-result" data-id="resilience">&larr; 返回结果</button>
      </nav>
      <div class="report-header" style="border-color: ${level.color}">
        <div class="level-badge" style="background-color: ${level.color}">${level.id}</div>
        <h2>${report.title}</h2>
      </div>
      <div class="report-section">
        <h3>总体评价</h3>
        <p>${report.evaluation}</p>
      </div>
      <div class="report-section">
        <h3>维度深度解读</h3>
        ${dimensionAnalysisHTML}
      </div>
      <div class="report-section">
        <h3>生活场景</h3>
        ${lifeScenes.map(s => `<div class="scene-item"><p>${s}</p></div>`).join('')}
      </div>
      <div class="report-section">
        <h3>改善行动</h3>
        ${actions.map((a, i) => `<div class="action-item"><span class="action-num">${i + 1}</span><p>${a}</p></div>`).join('')}
      </div>
      <div class="report-section">
        <h3>心理学小知识</h3>
        <p>${report.psychKnowledge}</p>
      </div>
      <div class="report-section counselor">
        <h3>咨询师寄语</h3>
        <p>${report.counselorNote}</p>
      </div>
      <div class="report-cta">
        <p>如需更深入的个人成长方案，可预约1对1咨询</p>
        <button class="btn btn-primary" data-action="contact-counselor">预约咨询</button>
      </div>
    </div>
  `;
}

/** 焦虑类型付费报告 */
function renderAnxietyPaidReport(assessment, scores, levelInfo) {
  let primaryTypeId;
  if (levelInfo.subtype === 'balanced') {
    primaryTypeId = levelInfo.sortedDimensions[0].dimensionId;
  } else if (levelInfo.subtype === 'dualHigh') {
    primaryTypeId = levelInfo.primary.dimensionId;
  } else {
    primaryTypeId = levelInfo.primary.dimensionId;
  }

  const report = assessment.paidReports[primaryTypeId];
  if (!report) return '<p>报告未找到</p>';

  const dimAnalysis = splitPipeSections(report.dimensionAnalysis);
  const lifeScenes = splitPipeSections(report.lifeScenes);
  const actions = splitPipeSections(report.actions);

  return `
    <div class="page page-paid-report fade-in">
      <nav class="back-nav">
        <button class="btn-back" data-action="go-result" data-id="anxiety">&larr; 返回结果</button>
      </nav>
      <div class="report-header" style="border-color: ${getTypeColor(primaryTypeId)}">
        <h2>${report.title}</h2>
      </div>
      <div class="report-section">
        <h3>你的焦虑在说什么</h3>
        <p>${report.yourAnxietySays}</p>
      </div>
      <div class="report-section">
        <h3>维度深度解读</h3>
        ${dimAnalysis.map(s => `<div class="report-section-item"><p>${s}</p></div>`).join('')}
      </div>
      <div class="report-section">
        <h3>生活场景</h3>
        ${lifeScenes.map(s => `<div class="scene-item"><p>${s}</p></div>`).join('')}
      </div>
      <div class="report-section">
        <h3>积极面</h3>
        <p>${report.positiveSide}</p>
      </div>
      <div class="report-section">
        <h3>改善行动</h3>
        ${actions.map((a, i) => `<div class="action-item"><span class="action-num">${i + 1}</span><p>${a}</p></div>`).join('')}
      </div>
      <div class="report-section">
        <h3>心理学小知识</h3>
        <p>${report.psychKnowledge}</p>
      </div>
      <div class="report-section counselor">
        <h3>咨询师寄语</h3>
        <p>${report.counselorNote}</p>
      </div>
      <div class="report-cta">
        <p>如需更深入的个人成长方案，可预约1对1咨询</p>
        <button class="btn btn-primary" data-action="contact-counselor">预约咨询</button>
      </div>
    </div>
  `;
}

/** 依附类型付费报告 */
function renderAttachmentPaidReport(assessment, scores, levelInfo) {
  const { attachmentType } = levelInfo;
  const report = assessment.paidReports[attachmentType.typeId];
  if (!report) return '<p>报告未找到</p>';

  const relationshipPatterns = splitPipeSections(report.relationshipPattern);
  const traps = splitPipeSections(report.traps);
  const actions = splitPipeSections(report.actions);

  return `
    <div class="page page-paid-report fade-in">
      <nav class="back-nav">
        <button class="btn-back" data-action="go-result" data-id="attachment">&larr; 返回结果</button>
      </nav>
      <div class="report-header" style="border-color: ${attachmentType.color}">
        <h2>${report.title}</h2>
      </div>
      <div class="report-section">
        <h3>你的依附风格</h3>
        <p>${report.yourStyle}</p>
      </div>
      <div class="report-section">
        <h3>你的爱的语言</h3>
        <p>${report.loveLanguage}</p>
      </div>
      <div class="report-section">
        <h3>关系模式</h3>
        ${relationshipPatterns.map(s => `<div class="scene-item"><p>${s}</p></div>`).join('')}
      </div>
      <div class="report-section">
        <h3>最佳伴侣匹配</h3>
        <p>${report.bestPartner}</p>
      </div>
      <div class="report-section">
        <h3>关系陷阱</h3>
        ${traps.map(t => `<div class="trap-item"><p>${t}</p></div>`).join('')}
      </div>
      <div class="report-section">
        <h3>改善行动</h3>
        ${actions.map((a, i) => `<div class="action-item"><span class="action-num">${i + 1}</span><p>${a}</p></div>`).join('')}
      </div>
      <div class="report-section">
        <h3>心理学小知识</h3>
        <p>${report.psychKnowledge}</p>
      </div>
      <div class="report-section counselor">
        <h3>咨询师寄语</h3>
        <p>${report.counselorNote}</p>
      </div>
      <div class="report-cta">
        <p>如需更深入的个人成长方案，可预约1对1咨询</p>
        <button class="btn btn-primary" data-action="contact-counselor">预约咨询</button>
      </div>
    </div>
  `;
}

/** 用 | 分割文本段落 */
function splitPipeSections(text) {
  return text.split('|').map(s => s.trim()).filter(Boolean);
}

// ==================== 页面渲染调度 ====================

function render() {
  const app = document.getElementById('app');
  let html = '';

  switch (state.currentPage) {
    case 'home':
      html = renderHome();
      break;
    case 'assessment-info':
      html = renderAssessmentInfo(state.currentAssessment);
      break;
    case 'quiz':
      html = renderQuiz(state.currentAssessment);
      break;
    case 'result':
      html = renderResult(state.currentAssessment, state.answers);
      break;
    case 'paid-report':
      html = renderPaidReport(state.currentAssessment, state.answers);
      break;
    default:
      html = renderHome();
  }

  app.innerHTML = html;
  scrollToTop();
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==================== 页面导航 ====================

function navigateTo(page, assessmentId = null) {
  state.currentPage = page;
  if (assessmentId !== null) {
    state.currentAssessment = assessmentId;
  }
  render();
}

// ==================== 事件处理 ====================

function handleAction(action, target) {
  const id = target.dataset.id;

  switch (action) {
    case 'select-assessment':
      navigateTo('assessment-info', id);
      break;

    case 'start-quiz':
      state.answers = {};
      state.currentQuestion = 0;
      state.quizState = 'active';
      navigateTo('quiz', id);
      break;

    case 'answer': {
      const qid = parseInt(target.dataset.qid, 10);
      const value = parseInt(target.dataset.value, 10);
      state.answers[qid] = value;

      // 更新选项UI - 移除其他selected，添加当前
      const container = target.closest('.options-grid');
      if (container) {
        container.querySelectorAll('.option-btn').forEach(btn => btn.classList.remove('selected'));
        target.classList.add('selected');
      }

      // 更新按钮状态
      const nextBtn = document.querySelector('[data-action="next-question"]');
      const viewResultBtn = document.querySelector('[data-action="view-result"]');
      if (nextBtn) nextBtn.disabled = false;
      if (viewResultBtn) viewResultBtn.disabled = false;
      break;
    }

    case 'next-question': {
      const a = assessments.find(a => a.id === state.currentAssessment);
      if (state.currentQuestion < a.questions.length - 1) {
        state.currentQuestion++;
        render();
      }
      break;
    }

    case 'prev-question':
      if (state.currentQuestion > 0) {
        state.currentQuestion--;
        render();
      }
      break;

    case 'view-result':
      state.quizState = 'completed';
      navigateTo('result', id);
      break;

    case 'go-home':
      navigateTo('home');
      break;

    case 'go-assessment-info':
      navigateTo('assessment-info', id);
      break;

    case 'go-result':
      navigateTo('result', id);
      break;

    case 'unlock-paid-report':
      navigateTo('paid-report', id);
      break;

    case 'retake':
      state.answers = {};
      state.currentQuestion = 0;
      state.quizState = 'idle';
      navigateTo('quiz', id);
      break;

    case 'share':
      if (navigator.share) {
        navigator.share({
          title: '亲密关系依附类型测试',
          text: '来测测你在亲密关系中的依附类型吧！',
          url: window.location.href
        }).catch(() => {});
      } else {
        // fallback: 复制链接
        navigator.clipboard.writeText(window.location.href).then(() => {
          const btn = target;
          const original = btn.textContent;
          btn.textContent = '链接已复制';
          setTimeout(() => { btn.textContent = original; }, 2000);
        }).catch(() => {});
      }
      break;

    case 'contact-counselor':
      // 预约咨询占位
      alert('预约咨询功能即将上线，敬请期待！');
      break;
  }
}

// ==================== 事件委托绑定 ====================

function bindEvents() {
  const app = document.getElementById('app');

  app.addEventListener('click', (e) => {
    const target = e.target.closest('[data-action]');
    if (!target) return;

    const action = target.dataset.action;
    handleAction(action, target);
  });
}

// ==================== 初始化 ====================

function init() {
  bindEvents();
  render();
}

document.addEventListener('DOMContentLoaded', init);

export { state, calculateScore, getLevel, reverseScore, render };
