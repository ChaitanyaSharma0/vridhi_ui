/**
 * VRIDDHI (वृद्धि) — Modern Editorial AI Response Renderer & Streaming Engine
 * 
 * Provides:
 * 1. Semantic Markdown rendering (headings, bold, italic, lists, code, quotes, tables, badges)
 * 2. Visual callout units (SKILL_UNLOCK, INSIGHT, METRIC, WARNING, RECOMMENDATION)
 * 3. Token/Word progressive block-aware streaming with smooth entrance animations
 * 4. User-friendly scroll-retention logic
 */

/**
 * Escapes HTML characters for safety
 */
export function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * Parses inline Markdown semantics:
 * - ***bold italic***
 * - **bold**
 * - *italic*
 * - `code`
 * - ==highlight==
 * - [+₹2.8L LPA] / [+6 jobs] (inline Vriddhi badges)
 * - [link text](url)
 */
export function parseInlineMarkdown(text) {
  if (!text) return '';

  let html = text;

  // 1. Triple bold + italic ***text***
  html = html.replace(/\*\*\*(.*?)\*\*\*/g, '<strong class="font-semibold italic text-stone-900">$1</strong>');

  // 2. Bold **text**
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-stone-900">$1</strong>');

  // 3. Italic *text* (avoid matching inside words or tags)
  html = html.replace(/(^|[^\*])\*([^\*\n]+)\*([^\*]|$)/g, '$1<em class="italic text-stone-700">$2</em>$3');

  // 4. Inline code `code`
  html = html.replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded bg-slate-100 text-[#3730a3] font-mono text-[13px] border border-slate-200/70">$1</code>');

  // 5. Text highlights ==highlight==
  html = html.replace(/==([^=]+)==/g, '<mark class="ai-highlight">$1</mark>');

  // 6. Inline metric badge: e.g. [+₹2.8L boost], [+6 matching jobs], [₹18.5L LPA], [P50 Median]
  html = html.replace(/\[(\+?[₹\$\d\w\.\s\-\%\+\/\(\)]+)\]/g, (match, p1) => {
    // Only turn into badge if it looks like a metric or growth figure
    if (/[₹\$\%\+]|\b(LPA|jobs|CTC|P50|P75|P25|IQR|Median)\b/i.test(p1)) {
      return `<span class="ai-inline-badge">${p1}</span>`;
    }
    return match;
  });

  // 7. Links [label](url)
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-[#4f46e5] underline underline-offset-2 hover:text-[#3730a3] font-medium">$1</a>');

  return html;
}

/**
 * Creates a minimal, elegant callout unit with smooth entrance animation
 */
export function createCalloutElement(type, data) {
  const el = document.createElement('div');
  el.className = 'ai-callout-unit my-3.5';

  switch (type.toLowerCase()) {
    case 'skill_unlock':
    case 'skill':
      el.innerHTML = `
        <div class="ai-card-skill">
          <div class="ai-card-skill-header">
            <div class="ai-card-skill-tag">
              <span class="ai-card-skill-icon">⚡</span>
              <span>${escapeHtml(data.tag || 'Skill Unlock')}</span>
            </div>
            ${data.badge ? `<span class="ai-card-skill-badge">${escapeHtml(data.badge)}</span>` : ''}
          </div>
          <div class="ai-card-skill-title">${escapeHtml(data.skill || data.title)}</div>
          <div class="ai-card-skill-pills">
            ${data.jobs ? `
              <span class="ai-pill-jobs">
                <span style="width: 7px; height: 7px; border-radius: 9999px; background: #10b981; display: inline-block;"></span>
                <span>${escapeHtml(data.jobs)}</span>
              </span>
            ` : ''}
            ${data.uplift ? `
              <span class="ai-pill-uplift">
                <span style="width: 7px; height: 7px; border-radius: 9999px; background: #2563eb; display: inline-block;"></span>
                <span>${escapeHtml(data.uplift)}</span>
              </span>
            ` : ''}
          </div>
          ${data.description ? `<p class="ai-card-skill-desc">${parseInlineMarkdown(data.description)}</p>` : ''}
        </div>
      `;
      break;

    case 'insight':
      el.innerHTML = `
        <div class="ai-card-insight">
          <div class="ai-card-insight-tag">
            <svg style="width: 1.05rem; height: 1.05rem; color: #0284c7; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">
              <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14H8a4 4 0 01-.9-7.898 4.004 4.004 0 017.8 0A4 4 0 0112 14z"/>
            </svg>
            <span>${escapeHtml(data.title || 'Market Signal')}</span>
          </div>
          <div class="ai-card-insight-text">
            ${parseInlineMarkdown(data.text || data.description)}
          </div>
        </div>
      `;
      break;

    case 'metric':
      el.innerHTML = `
        <div class="ai-card-metric">
          <span class="ai-card-metric-label">${escapeHtml(data.label || 'Market Benchmark')}</span>
          <span class="ai-card-metric-value">${escapeHtml(data.value)}</span>
          ${data.subtext ? `<span class="ai-card-metric-subtext">${parseInlineMarkdown(data.subtext)}</span>` : ''}
        </div>
      `;
      break;

    case 'warning':
    case 'gap':
      el.innerHTML = `
        <div class="ai-card-warning">
          <div class="ai-card-warn-tag">
            <svg style="width: 1.05rem; height: 1.05rem; color: #f43f5e; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>
            <span>${escapeHtml(data.title || 'Critical Gap')}</span>
          </div>
          <div class="ai-card-warn-text">
            ${parseInlineMarkdown(data.text || data.description)}
          </div>
        </div>
      `;
      break;

    case 'recommendation':
      el.innerHTML = `
        <div class="ai-card-recommendation">
          <div class="ai-card-rec-tag">
            <svg style="width: 1.05rem; height: 1.05rem; color: #10b981; flex-shrink: 0;" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
            <span>${escapeHtml(data.title || 'Recommendation')}</span>
          </div>
          <div class="ai-card-rec-text">
            ${parseInlineMarkdown(data.text || data.description)}
          </div>
        </div>
      `;
      break;

    default:
      el.innerHTML = `
        <div class="rounded-xl bg-stone-50 border border-stone-200 p-3.5 max-w-2xl">
          <div class="text-xs font-semibold text-stone-700 mb-1">${escapeHtml(data.title || 'Note')}</div>
          <div class="text-[13.5px] text-stone-800">${parseInlineMarkdown(data.text || data.description || '')}</div>
        </div>
      `;
      break;
  }

  return el;
}

/**
 * Creates a clean responsive comparison table
 */
export function createTableElement(headers, rows) {
  const container = document.createElement('div');
  container.className = 'ai-callout-unit ai-table-wrapper my-4 overflow-x-auto rounded-xl border border-stone-200/80 bg-white shadow-2xs max-w-3xl';

  const table = document.createElement('table');
  table.className = 'w-full text-left text-xs sm:text-[13.5px] border-collapse';

  // Table Head
  const thead = document.createElement('thead');
  thead.className = 'bg-stone-50/90 border-b border-stone-200 text-stone-700 font-semibold';
  thead.innerHTML = `
    <tr>
      ${headers.map(h => `<th class="py-2.5 px-3.5 font-semibold text-stone-800">${escapeHtml(h)}</th>`).join('')}
    </tr>
  `;
  table.appendChild(thead);

  // Table Body
  const tbody = document.createElement('tbody');
  tbody.className = 'divide-y divide-stone-100 text-stone-800';
  rows.forEach(row => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-stone-50/60 transition-colors';
    tr.innerHTML = row.map(cell => `<td class="py-2.5 px-3.5 leading-relaxed">${parseInlineMarkdown(cell)}</td>`).join('');
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);

  container.appendChild(table);
  return container;
}

/**
 * Creates a modern code block with copy button
 */
export function createCodeElement(language, code) {
  const container = document.createElement('div');
  container.className = 'ai-callout-unit ai-code-wrapper my-4 rounded-xl overflow-hidden border border-stone-800 bg-[#18181b] shadow-xs text-xs font-mono max-w-2xl';

  const header = document.createElement('div');
  header.className = 'flex items-center justify-between px-3.5 py-2 bg-[#27272a] text-stone-300 border-b border-stone-700/60';
  header.innerHTML = `
    <span class="text-[11px] font-sans font-medium uppercase tracking-wider text-stone-400">${escapeHtml(language || 'code')}</span>
    <button class="ai-copy-btn text-[11px] font-sans px-2.5 py-1 rounded bg-stone-700/80 hover:bg-stone-600 text-stone-200 transition-colors flex items-center gap-1.5 cursor-pointer">
      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
      <span>Copy</span>
    </button>
  `;

  const pre = document.createElement('pre');
  pre.className = 'p-3.5 overflow-x-auto text-stone-200 leading-relaxed font-mono text-[12.5px]';
  const codeEl = document.createElement('code');
  codeEl.textContent = code.trim();
  pre.appendChild(codeEl);

  container.appendChild(header);
  container.appendChild(pre);

  // Setup copy interaction
  const copyBtn = header.querySelector('.ai-copy-btn');
  copyBtn?.addEventListener('click', () => {
    navigator.clipboard?.writeText(code.trim()).then(() => {
      copyBtn.innerHTML = `
        <svg class="w-3 h-3 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
        <span class="text-emerald-400">Copied!</span>
      `;
      setTimeout(() => {
        copyBtn.innerHTML = `
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
          <span>Copy</span>
        `;
      }, 2000);
    });
  });

  return container;
}

/**
 * Parses raw multi-line Markdown into a structured array of renderable blocks
 */
export function markdownToBlocks(markdown) {
  if (!markdown) return [];

  const lines = markdown.split('\n');
  const blocks = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Blank line
    if (!line.trim()) {
      i++;
      continue;
    }

    // Code block ```
    if (line.trim().startsWith('```')) {
      const lang = line.trim().slice(3).trim();
      const codeLines = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // skip closing ```
      blocks.push({
        type: 'code',
        language: lang,
        code: codeLines.join('\n')
      });
      continue;
    }

    // Markdown Table (starts with |)
    if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
      const tableLines = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        tableLines.push(lines[i].trim());
        i++;
      }
      if (tableLines.length >= 2) {
        const parseRow = (r) => r.split('|').slice(1, -1).map(c => c.trim());
        const headers = parseRow(tableLines[0]);
        // line 1 is usually separator | --- | --- |
        const dataRows = [];
        for (let j = 1; j < tableLines.length; j++) {
          if (tableLines[j].includes('---')) continue;
          dataRows.push(parseRow(tableLines[j]));
        }
        blocks.push({
          type: 'table',
          headers,
          rows: dataRows
        });
      }
      continue;
    }

    // Headings
    if (line.startsWith('#')) {
      const match = line.match(/^(#{1,6})\s+(.*)$/);
      if (match) {
        blocks.push({
          type: 'heading',
          level: match[1].length,
          text: match[2]
        });
        i++;
        continue;
      }
    }

    // Blockquote >
    if (line.startsWith('>')) {
      const quoteLines = [];
      while (i < lines.length && lines[i].startsWith('>')) {
        quoteLines.push(lines[i].replace(/^>\s?/, ''));
        i++;
      }
      blocks.push({
        type: 'quote',
        text: quoteLines.join('\n')
      });
      continue;
    }

    // Unordered List (- or *)
    if (/^\s*[\-\*]\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*[\-\*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[\-\*]\s+/, ''));
        i++;
      }
      blocks.push({
        type: 'list',
        ordered: false,
        items
      });
      continue;
    }

    // Ordered List (1. 2.)
    if (/^\s*\d+\.\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+\.\s+/, ''));
        i++;
      }
      blocks.push({
        type: 'list',
        ordered: true,
        items
      });
      continue;
    }

    // Horizontal separator
    if (/^(\-\-\-|\*\*\*|___)\s*$/.test(line)) {
      blocks.push({ type: 'hr' });
      i++;
      continue;
    }

    // Custom Callout directive:
    // :::callout-type
    // Title
    // Text
    // :::
    if (line.trim().startsWith(':::callout-')) {
      const calloutType = line.trim().replace(':::callout-', '').trim();
      const calloutLines = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith(':::')) {
        calloutLines.push(lines[i]);
        i++;
      }
      i++; // skip closing :::
      blocks.push({
        type: 'callout',
        calloutType,
        data: {
          title: calloutLines[0] || '',
          text: calloutLines.slice(1).join('\n')
        }
      });
      continue;
    }

    // Normal prose paragraph
    const paraLines = [];
    while (i < lines.length && lines[i].trim() && !lines[i].startsWith('#') && !lines[i].startsWith('>') && !lines[i].startsWith('```') && !lines[i].startsWith('|') && !/^\s*[\-\*]\s+/.test(lines[i]) && !/^\s*\d+\.\s+/.test(lines[i]) && !lines[i].startsWith(':::')) {
      paraLines.push(lines[i]);
      i++;
    }
    blocks.push({
      type: 'prose',
      text: paraLines.join(' ')
    });
  }

  return blocks;
}

/**
 * Progressive Block-Aware Streaming Engine
 * 
 * Streams text word-by-word / chunk-by-chunk with a soft blinking cursor,
 * and reveals structured callouts/tables/code as coherent animated visual units.
 * 
 * Never restarts or re-renders completed blocks.
 * Respects manual user scroll position.
 */
export async function streamBlocks({
  container,
  blocks,
  scrollContainer,
  onComplete,
  wordDelay = 18
}) {
  if (!container || !blocks || !blocks.length) {
    onComplete?.();
    return;
  }

  // Smart scroll helper: only auto-scroll if user is currently near the bottom
  const smartScroll = () => {
    if (!scrollContainer) return;
    const distanceToBottom = scrollContainer.scrollHeight - scrollContainer.scrollTop - scrollContainer.clientHeight;
    if (distanceToBottom < 120) {
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
    }
  };

  // Helper delay
  const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  for (let blockIdx = 0; blockIdx < blocks.length; blockIdx++) {
    const block = blocks[blockIdx];

    switch (block.type) {
      case 'prose': {
        const p = document.createElement('p');
        p.className = 'mb-3.5 leading-relaxed text-[#242b35] font-normal';
        container.appendChild(p);

        // Stream word by word
        const words = block.text.split(/(\s+)/);
        let accumulated = '';

        for (let w = 0; w < words.length; w++) {
          accumulated += words[w];
          p.innerHTML = parseInlineMarkdown(accumulated) + '<span class="ai-stream-cursor"></span>';
          smartScroll();
          if (words[w].trim()) {
            await wait(wordDelay);
          }
        }

        // Finalize paragraph without cursor
        p.innerHTML = parseInlineMarkdown(accumulated);
        break;
      }

      case 'heading': {
        const tag = block.level === 1 ? 'h1' : block.level === 2 ? 'h2' : 'h3';
        const heading = document.createElement(tag);
        if (block.level === 1) {
          heading.className = 'text-xl sm:text-2xl font-semibold text-stone-900 mt-5 mb-2 tracking-tight';
        } else if (block.level === 2) {
          heading.className = 'text-lg sm:text-xl font-semibold text-stone-900 mt-4 mb-2 tracking-tight';
        } else {
          heading.className = 'text-base sm:text-lg font-semibold text-stone-900 mt-3.5 mb-1.5 tracking-tight';
        }
        container.appendChild(heading);

        const words = block.text.split(/(\s+)/);
        let accumulated = '';

        for (let w = 0; w < words.length; w++) {
          accumulated += words[w];
          heading.innerHTML = parseInlineMarkdown(accumulated) + '<span class="ai-stream-cursor"></span>';
          smartScroll();
          if (words[w].trim()) {
            await wait(wordDelay);
          }
        }
        heading.innerHTML = parseInlineMarkdown(accumulated);
        break;
      }

      case 'list': {
        const listEl = document.createElement(block.ordered ? 'ol' : 'ul');
        if (block.ordered) {
          listEl.className = 'my-3 space-y-1.5 pl-5 list-decimal marker:text-stone-600 marker:font-medium text-[#2d3748]';
        } else {
          listEl.className = 'my-3 space-y-1.5 pl-5 list-disc marker:text-[#6366f1] text-[#2d3748]';
        }
        container.appendChild(listEl);

        for (let itemIdx = 0; itemIdx < block.items.length; itemIdx++) {
          const itemText = block.items[itemIdx];
          const li = document.createElement('li');
          li.className = 'leading-relaxed text-[#2d3748]';
          listEl.appendChild(li);

          const words = itemText.split(/(\s+)/);
          let accumulated = '';

          for (let w = 0; w < words.length; w++) {
            accumulated += words[w];
            li.innerHTML = parseInlineMarkdown(accumulated) + '<span class="ai-stream-cursor"></span>';
            smartScroll();
            if (words[w].trim()) {
              await wait(wordDelay);
            }
          }
          li.innerHTML = parseInlineMarkdown(accumulated);
          await wait(40);
        }
        break;
      }

      case 'quote': {
        const quoteEl = document.createElement('blockquote');
        quoteEl.className = 'border-l-3 border-[#6366f1]/60 pl-3.5 my-3 italic text-slate-700 bg-[#f8fafc] py-1.5 rounded-r-lg';
        container.appendChild(quoteEl);

        const words = block.text.split(/(\s+)/);
        let accumulated = '';

        for (let w = 0; w < words.length; w++) {
          accumulated += words[w];
          quoteEl.innerHTML = parseInlineMarkdown(accumulated) + '<span class="ai-stream-cursor"></span>';
          smartScroll();
          if (words[w].trim()) {
            await wait(wordDelay);
          }
        }
        quoteEl.innerHTML = parseInlineMarkdown(accumulated);
        break;
      }

      case 'callout': {
        // Subtle pause before revealing callout as complete unit
        await wait(120);
        const calloutEl = createCalloutElement(block.calloutType, block.data);
        container.appendChild(calloutEl);
        smartScroll();
        // Wait for entrance animation to comfortably settle
        await wait(240);
        break;
      }

      case 'table': {
        await wait(120);
        const tableEl = createTableElement(block.headers, block.rows);
        container.appendChild(tableEl);
        smartScroll();
        await wait(220);
        break;
      }

      case 'code': {
        await wait(120);
        const codeEl = createCodeElement(block.language, block.code);
        container.appendChild(codeEl);
        smartScroll();
        await wait(220);
        break;
      }

      case 'hr': {
        const hr = document.createElement('hr');
        hr.className = 'my-4 border-stone-200/80';
        container.appendChild(hr);
        break;
      }
    }
  }

  // Remove any remaining stream cursor
  container.querySelectorAll('.ai-stream-cursor').forEach(c => c.remove());
  smartScroll();

  onComplete?.();
}
