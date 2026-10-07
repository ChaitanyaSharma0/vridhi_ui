/**
 * VRIDDHI (वृद्धि) — DEDICATED FULL-SCREEN AI COUNSELOR
 * Architecture:
 * VriddhiAI
 * ├── AILanding
 * │   ├── AIAtmosphere (Layered Radial Gradients: Orange, Peach, Lavender, Center Glow)
 * │   ├── AIBranding (Hero Title in Instrument Serif + Subtitle)
 * │   └── AIPrompt (Category Capability Pills + Prompt Chips)
 * ├── PersistentComposer (Shared, single persistent DOM element physically translating)
 * └── AIConversation
 *     ├── Messages (Clean editorial thread)
 *     ├── AIResponse (Structured roadmap cards with official lotus icon)
 *     └── FollowupChips (Contextual follow-up actions)
 */

import { store } from './state.js';
import { CAREER_ROLES, CITIES } from '../data/mockData.js';
import { streamBlocks, markdownToBlocks, escapeHtml } from './aiResponseRenderer.js';
import { loadingAnimationData } from './loadingAnimationData.js';

let isAIOpen = false;
let hasStartedConversation = false;
let currentLottieAnim = null;

export function initAICounselor() {
  const platformView = document.getElementById('platform-view');
  const aiView = document.getElementById('vriddhi-ai-view');
  const aiAtmosphere = document.getElementById('ai-workspace') || document.getElementById('vriddhi-ai-view');
  const landingHero = document.getElementById('ai-landing-hero');
  const conversationScroll = document.getElementById('ai-conversation-scroll');
  const messagesContainer = document.getElementById('ai-conversation-messages');
  const persistentForm = document.getElementById('ai-persistent-form');
  const persistentInput = document.getElementById('ai-persistent-input');
  const btnBack = document.getElementById('btn-ai-back');
  const btnBackLogo = document.getElementById('btn-ai-back-logo');
  const btnNewChat = document.getElementById('btn-ai-new-chat');
  const metroSelect = document.getElementById('ai-metro-select');

  let isGenerating = false;

  if (!aiView || !persistentInput) return;

  // Metro select synchronization
  if (metroSelect) {
    metroSelect.value = store.getState().selectedCity || 'bengaluru';
    metroSelect.addEventListener('change', (e) => {
      store.setState({ selectedCity: e.target.value });
      const globalSelect = document.getElementById('global-city-select');
      if (globalSelect) globalSelect.value = e.target.value;
    });
  }

  let savedScrollY = 0;
  let transitionTimeout = null;

  // Open Full-Screen AI with Cinematic Smooth Transitions
  window.openVriddhiAI = function(initialQuery = null) {
    if (isAIOpen) {
      if (initialQuery) handleUserSubmit(initialQuery);
      return;
    }

    isAIOpen = true;
    if (transitionTimeout) {
      clearTimeout(transitionTimeout);
      transitionTimeout = null;
    }

    // 1. Capture platform view scroll offset so returning restores exact position
    savedScrollY = window.scrollY || document.documentElement.scrollTop || 0;

    // 2. Prevent scroll chaining during full-screen AI mode
    document.body.style.overflow = 'hidden';

    // 3. Prepare AI View & Platform View for concurrent smooth transitions
    aiView.style.opacity = '';
    aiView.style.transform = '';
    aiView.classList.remove('hidden', 'ai-closing');
    if (platformView) {
      platformView.style.visibility = 'visible';
      platformView.classList.add('platform-dimmed');
    }

    // 4. Trigger the AI entrance animation (staggered cards, canopy, lotus, title, composer)
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        aiView.classList.add('ai-active');
      });
    });

    // 5. Once the 450ms zoom/fade transition completes, hide platform view from screen readers/tab focus
    transitionTimeout = setTimeout(() => {
      if (isAIOpen && platformView) {
        platformView.style.visibility = 'hidden';
      }
    }, 480);

    // Hash sync
    if (window.location.hash !== '#ai-counselor') {
      history.pushState(null, '', '#ai-counselor');
    }

    if (initialQuery) {
      handleUserSubmit(initialQuery);
    } else {
      setTimeout(() => persistentInput?.focus(), 350);
    }
  };

  // Close Full-Screen AI (Smooth Return to Platform)
  window.closeVriddhiAI = function() {
    if (!isAIOpen) return;
    isAIOpen = false;
    if (transitionTimeout) {
      clearTimeout(transitionTimeout);
      transitionTimeout = null;
    }

    // 1. Make platform view visible again and instantly restore user scroll position
    if (platformView) {
      platformView.style.visibility = 'visible';
      window.scrollTo(0, savedScrollY);
      // Remove dimmed class to smoothly scale & fade platform back in
      requestAnimationFrame(() => {
        platformView.classList.remove('platform-dimmed');
      });
    }

    // 2. Initiate AI exit animation
    aiView.style.opacity = '';
    aiView.style.transform = '';
    aiView.classList.remove('ai-active');
    aiView.classList.add('ai-closing');
    document.body.style.overflow = '';

    // 3. Clean up after exit animation completes (~450ms)
    transitionTimeout = setTimeout(() => {
      aiView.classList.remove('ai-closing');
    }, 480);

    if (window.location.hash === '#ai-counselor') {
      history.pushState(null, '', window.location.pathname);
    }
  };

  // Back actions
  btnBack?.addEventListener('click', () => window.closeVriddhiAI());
  btnBackLogo?.addEventListener('click', (e) => {
    e.preventDefault();
    window.closeVriddhiAI();
  });

  // Attach all trigger buttons across the platform
  document.querySelectorAll('.btn-open-counselor').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const initialPrompt = btn.dataset.prompt || null;
      window.openVriddhiAI(initialPrompt);
    });
  });

  // Category Capability Pills (Landing)
  document.querySelectorAll('.ai-category-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      if (isGenerating) return;
      const query = pill.dataset.query || pill.textContent.trim();
      handleUserSubmit(query);
    });
  });

  // Persistent Form Submission (Single shared composer with generation lock)
  persistentForm?.addEventListener('submit', (e) => {
    e.preventDefault();
    if (isGenerating) return;
    const query = persistentInput.value.trim();
    if (!query) return;
    persistentInput.value = '';
    handleUserSubmit(query);
  });

  // Prevent multiple enter submissions while generating
  persistentInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey && isGenerating) {
      e.preventDefault();
    }
  });

  // New Chat / Reset
  btnNewChat?.addEventListener('click', resetToLanding);

  // Keyboard navigation: Escape key closes AI
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isAIOpen) {
      window.closeVriddhiAI();
    }
  });

  // Window hash change routing
  window.addEventListener('hashchange', () => {
    if (window.location.hash === '#ai-counselor' || window.location.hash === '#counselor') {
      window.openVriddhiAI();
    } else if (isAIOpen) {
      window.closeVriddhiAI();
    }
  });

  // Initial check on page load
  if (window.location.hash === '#ai-counselor' || window.location.hash === '#counselor') {
    window.openVriddhiAI();
  }

  /**
   * Helper: Lock/Unlock UI During AI Generation
   */
  function setGeneratingState(generating) {
    isGenerating = generating;
    if (generating) {
      if (persistentInput) {
        persistentInput.disabled = true;
        persistentInput.placeholder = 'Vriddhi AI is generating your response...';
      }
      persistentForm?.classList.add('ai-input-disabled');
      const sendBtn = persistentForm?.querySelector('.ai-send-btn');
      if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.classList.add('opacity-40', 'cursor-not-allowed', 'pointer-events-none');
      }
      removeAllResponseSuggestions();
    } else {
      if (persistentInput) {
        persistentInput.disabled = false;
        persistentInput.placeholder = hasStartedConversation ? 'Ask a follow-up question...' : 'Ask Vriddhi anything about your career...';
      }
      persistentForm?.classList.remove('ai-input-disabled');
      const sendBtn = persistentForm?.querySelector('.ai-send-btn');
      if (sendBtn) {
        sendBtn.disabled = false;
        sendBtn.classList.remove('opacity-40', 'cursor-not-allowed', 'pointer-events-none');
      }
      persistentInput?.focus();
    }
  }

  /**
   * Remove any active suggestion cards attached to prior responses
   */
  function removeAllResponseSuggestions() {
    document.querySelectorAll('.ai-response-suggestions').forEach(el => el.remove());
  }

  /**
   * Generates Contextual Follow-up Suggestions based on query topic
   * Formatted strictly like user Gemini reference: two rich, side-by-side questions with ↳
   */
  function getContextualSuggestions(query, state) {
    const q = (query || '').toLowerCase();

    // 1. Data Science / ML / Deep Learning / AI
    if (q.includes('data science') || q.includes('data scientist') || q.includes('machine learning') || q.includes('mlops') || q.includes('pytorch') || q.includes('llm')) {
      return [
        "Draft a 6-month roadmap to switch from Analyst to Data Engineer",
        "Compare skill requirements for PyTorch vs. LangChain vs. Triton"
      ];
    }

    // 2. SDE vs Data Analyst / Salary / CTC / Compensation
    if (q.includes('sde') || q.includes('data analyst') || q.includes('salary') || q.includes('salaries') || q.includes('compensation') || q.includes('ctc') || q.includes('percentile')) {
      return [
        "Draft a 6-month roadmap to switch from Analyst to Data Engineer",
        "Compare skill requirements for dbt vs. Airflow vs. PySpark"
      ];
    }

    // 3. BCA / Degree / College / MCA / Freshers
    if (q.includes('bca') || q.includes('degree') || q.includes('worth it') || q.includes('mca') || q.includes('college') || q.includes('fresher') || q.includes('btech')) {
      return [
        "Draft high-converting portfolio projects for off-campus product roles",
        "Compare entry compensation: MCA degree vs. 2 years product experience"
      ];
    }

    // 4. Product Management / APM / PM
    if (q.includes('product manager') || q.includes('pm') || q.includes('apm')) {
      return [
        "Draft a teardown case study for an Indian fintech product flow",
        "Compare APM eligibility requirements across Swiggy, Razorpay, and Cred"
      ];
    }

    // 5. Metro / City Comparison / Pune / Bengaluru / Hyderabad / Relocation
    if (q.includes('pune') || q.includes('bengaluru') || q.includes('hyderabad') || q.includes('ncr') || q.includes('mumbai') || q.includes('living cost') || q.includes('rent') || q.includes('relocation')) {
      return [
        "Compare net savings: ₹16L in Pune vs. ₹18.5L in Bengaluru",
        "Draft negotiation email script for an Indian metro relocation bonus"
      ];
    }

    // 6. Python / Code / Script / Algorithm / Tukey IQR
    if (q.includes('python') || q.includes('code') || q.includes('script') || q.includes('iqr') || q.includes('tukey') || q.includes('algorithm')) {
      return [
        "Draft a Python script to filter compensation percentiles using Tukey IQR",
        "Compare salary spreads between product MNCs and GCC firms in Bengaluru"
      ];
    }

    // 7. 3-Month Plan / Learning Plan / Roadmap / Transition
    if (q.includes('3-month') || q.includes('learning plan') || q.includes('roadmap') || q.includes('plan') || q.includes('timeline')) {
      return [
        "Draft week-by-week production deliverables for Month 1 pipeline sprint",
        "Compare interview system design expectations for SDE-1 vs. SDE-2"
      ];
    }

    // Default contextual pair matching user reference
    return [
      "Draft a 6-month roadmap to switch from Analyst to Data Engineer",
      "Compare skill requirements for dbt vs. Airflow vs. PySpark"
    ];
  }

  /**
   * Render Gemini-Style Topic Suggestion Cards directly ATTACHED to the end of the AI Response
   */
  function renderAttachedResponseSuggestions(responseEl, query, state) {
    if (!responseEl) return;
    const suggestions = getContextualSuggestions(query, state);
    if (!suggestions || suggestions.length === 0) return;

    // Remove any previously rendered suggestions in any other message
    removeAllResponseSuggestions();

    const bodyEl = responseEl.querySelector('.ai-response-body');
    if (!bodyEl) return;

    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'ai-response-suggestions mt-6 pt-1 w-full animate-fade-in';
    suggestionsContainer.innerHTML = `
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-3 w-full">
        ${suggestions.map(text => `
          <button type="button" class="ai-suggestion-card group" data-query="${escapeHtml(text)}" title="Ask: ${escapeHtml(text)}">
            <span class="ai-suggestion-card-text">${escapeHtml(text)}</span>
            <div class="ai-suggestion-card-arrow">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 5v6a3 3 0 003 3h11m0 0l-3.5-3.5M18 14l-3.5 3.5" />
              </svg>
            </div>
          </button>
        `).join('')}
      </div>
    `;

    bodyEl.appendChild(suggestionsContainer);

    // Attach click handler for these suggestion cards
    suggestionsContainer.addEventListener('click', (e) => {
      const card = e.target.closest('.ai-suggestion-card');
      if (!card || isGenerating) return;
      const nextQuery = card.dataset.query || card.querySelector('.ai-suggestion-card-text')?.textContent.trim();
      if (nextQuery) {
        removeAllResponseSuggestions();
        handleUserSubmit(nextQuery);
      }
    });

    scrollToBottom();
  }

  /**
   * Main User Query Submission Orchestrator
   */
  function handleUserSubmit(query) {
    if (!query || isGenerating) return;

    if (!isAIOpen) {
      window.openVriddhiAI(query);
      return;
    }

    // Always remove existing suggestions whenever a new question is submitted
    removeAllResponseSuggestions();

    // Lock input until response stream completely finishes
    setGeneratingState(true);

    // If still in Landing state, trigger continuous physical transition
    if (!hasStartedConversation) {
      transitionToConversation(query);
    } else {
      appendUserMessage(query);
      triggerAIResponse(query);
    }
  }

  /**
   * Physical Transition from AILanding to AIConversation
   * The SAME input pill physically glides from center to bottom!
   */
  function transitionToConversation(firstQuery) {
    hasStartedConversation = true;

    // 1. Atmospheric gradient smoothly travels downward to frame composer & header frost activates
    aiAtmosphere?.classList.add('conversation-mode');
    aiView?.classList.add('conversation-mode');

    // 2. Landing hero section collapses upward
    if (landingHero) {
      landingHero.style.maxHeight = '0px';
      landingHero.style.opacity = '0';
      landingHero.style.transform = 'translateY(-30px)';
      landingHero.style.pointerEvents = 'none';
      landingHero.style.marginBottom = '0px';
      landingHero.style.paddingTop = '0px';
      landingHero.style.paddingBottom = '0px';
    }

    // 3. Conversation scroll container expands above composer strictly below header
    if (conversationScroll) {
      conversationScroll.classList.remove('h-0', 'max-h-0', 'opacity-0', 'pointer-events-none');
      conversationScroll.classList.add('flex-1', 'opacity-100');
      conversationScroll.style.maxHeight = '100%';
    }

    // 4. Update composer placeholder
    if (persistentInput) {
      persistentInput.placeholder = 'Ask a follow-up question...';
    }

    // 5. Inject first user query & AI response
    appendUserMessage(firstQuery);
    triggerAIResponse(firstQuery);
    setTimeout(() => persistentInput?.focus(), 400);
  }

  /**
   * Reset Conversation back to AILanding
   * The persistent composer physically slides back to the center!
   */
  function resetToLanding() {
    hasStartedConversation = false;
    setGeneratingState(false);
    removeAllResponseSuggestions();

    store.setState({ chatMessages: [] });
    if (messagesContainer) messagesContainer.innerHTML = '';

    // 1. Atmospheric gradient returns to top-center & header resets
    aiAtmosphere?.classList.remove('conversation-mode');
    aiView?.classList.remove('conversation-mode');

    // 2. Collapse conversation scroll container
    if (conversationScroll) {
      conversationScroll.classList.add('h-0', 'max-h-0', 'opacity-0', 'pointer-events-none');
      conversationScroll.classList.remove('flex-1', 'opacity-100');
      conversationScroll.style.maxHeight = '0px';
    }

    // 3. Expand landing hero back to open spacious state
    if (landingHero) {
      landingHero.style.maxHeight = '';
      landingHero.style.opacity = '1';
      landingHero.style.transform = 'none';
      landingHero.style.pointerEvents = 'auto';
      landingHero.style.marginBottom = '';
      landingHero.style.paddingTop = '';
      landingHero.style.paddingBottom = '';
    }

    // 4. Reset composer placeholder & focus
    if (persistentInput) {
      persistentInput.placeholder = 'Ask Vriddhi anything about your career...';
      persistentInput.value = '';
      persistentInput.focus();
    }
  }

  /**
   * Append User Message into Messages Container
   */
  /**
   * Append User Message into Messages Container
   */
  function appendUserMessage(text) {
    if (!messagesContainer) return;
    const userMsgEl = document.createElement('div');
    userMsgEl.className = 'flex items-start justify-end gap-3 animate-fade-in';
    userMsgEl.innerHTML = `
      <div class="ai-user-bubble">
        ${escapeHtml(text)}
      </div>
      <div class="ai-user-avatar">
        <svg class="w-5.5 h-5.5 text-white" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
        </svg>
      </div>
    `;
    messagesContainer.appendChild(userMsgEl);
    scrollToBottom();
  }

  /**
   * Trigger AI Response with Lottie Animation Delay & Progressive Streaming
   * Shows loading.json animation first for a few seconds before streaming response.
   */
  function triggerAIResponse(query) {
    showTypingIndicator();

    // Show loading.json animation for ~2.5 seconds before streaming
    const delayMs = 2500;

    setTimeout(() => {
      removeTypingIndicator();
      const responseData = generateStructuredAIResponse(query, store.getState());
      renderStructuredResponse(responseData, query);
    }, delayMs);
  }

  /**
   * Loading State with Lottie Animation (loading.json) & Lotus Avatar
   */
  function showTypingIndicator() {
    if (!messagesContainer) return;
    removeTypingIndicator();

    const typingEl = document.createElement('div');
    typingEl.id = 'ai-typing-indicator';
    typingEl.className = 'ai-message-row flex items-start gap-3.5 sm:gap-4 max-w-3xl mx-auto w-full my-4 animate-fade-in';
    typingEl.innerHTML = `
      <!-- Official Lotus Avatar in Vivid Gradient Badge -->
      <div class="ai-avatar-badge">
        <img src="public/assets/vriddhi/lotus.svg" alt="Vriddhi AI" />
      </div>

      <!-- Pure Lottie Animation (No box, no text) -->
      <div id="vriddhi-lottie-container" class="vriddhi-lottie-container w-10 h-10 flex items-center justify-center mt-0.5">
        <!-- Fallback bouncing dots while Lottie initializes -->
        <div class="ai-lottie-fallback flex items-center gap-1.5">
          <span class="w-1.5 h-1.5 rounded-full bg-[#6366f1] animate-bounce"></span>
          <span class="w-1.5 h-1.5 rounded-full bg-[#6366f1] animate-bounce [animation-delay:0.2s]"></span>
          <span class="w-1.5 h-1.5 rounded-full bg-[#6366f1] animate-bounce [animation-delay:0.4s]"></span>
        </div>
      </div>
    `;
    messagesContainer.appendChild(typingEl);
    scrollToBottom();

    // Mount Lottie animation from loading.json
    const lottieContainer = document.getElementById('vriddhi-lottie-container');
    if (lottieContainer) {
      const renderLottie = () => {
        if (window.lottie && loadingAnimationData) {
          lottieContainer.innerHTML = '';
          currentLottieAnim = window.lottie.loadAnimation({
            container: lottieContainer,
            renderer: 'svg',
            loop: true,
            autoplay: true,
            animationData: loadingAnimationData
          });
        }
      };

      if (window.lottie) {
        renderLottie();
      } else {
        // Wait for lottie script if still loading
        const pollInterval = setInterval(() => {
          if (window.lottie) {
            clearInterval(pollInterval);
            renderLottie();
          }
        }, 50);
        setTimeout(() => clearInterval(pollInterval), 3000);
      }
    }
  }

  function removeTypingIndicator() {
    if (currentLottieAnim) {
      try {
        currentLottieAnim.destroy();
      } catch (err) {}
      currentLottieAnim = null;
    }
    const el = document.getElementById('ai-typing-indicator');
    el?.remove();
  }

  /**
   * Render AI Response as Natural Editorial Typography
   * NO large wrapping card. Typography-first with selective callouts and block-aware streaming.
   */
  function renderStructuredResponse(data, query) {
    if (!messagesContainer) return;

    // Create Assistant Row (Lotus icon on left, unboxed prose container on right)
    const assistantMsgEl = document.createElement('div');
    assistantMsgEl.className = 'ai-message-row flex items-start gap-3.5 sm:gap-4 max-w-3xl mx-auto w-full my-4';

    assistantMsgEl.innerHTML = `
      <!-- Official Lotus Avatar in Vivid Gradient Badge -->
      <div class="ai-avatar-badge">
        <img src="public/assets/vriddhi/lotus.svg" alt="Vriddhi AI" />
      </div>

      <!-- Natural Editorial Prose Flow (NO CARD/BOX WRAPPER!) -->
      <div class="ai-response-body flex-1 min-w-0 text-[15px] sm:text-[15.5px] leading-[1.75] text-[#242b35] font-sans">
      </div>
    `;

    messagesContainer.appendChild(assistantMsgEl);
    const bodyEl = assistantMsgEl.querySelector('.ai-response-body');

    // Extract or normalize blocks
    let blocks = [];
    if (data.blocks && Array.isArray(data.blocks)) {
      blocks = data.blocks;
    } else if (data.rawMarkdown) {
      blocks = markdownToBlocks(data.rawMarkdown);
    } else {
      // Graceful fallback for legacy structure
      if (data.intro) blocks.push({ type: 'prose', text: data.intro });
      if (data.cards && Array.isArray(data.cards)) {
        data.cards.forEach(card => {
          blocks.push({
            type: 'callout',
            calloutType: 'insight',
            data: {
              title: card.title,
              text: card.items?.map(i => `${i.label}: **${i.tag}**`).join(' · ') || ''
            }
          });
        });
      }
      if (data.outro) blocks.push({ type: 'prose', text: data.outro });
    }

    scrollToBottom();

    // Stream blocks progressively
    streamBlocks({
      container: bodyEl,
      blocks: blocks,
      scrollContainer: messagesContainer,
      onComplete: () => {
        // Unlock user input so they can send follow-ups
        setGeneratingState(false);
        // Display Gemini-style suggestions contextual to the topic, ATTACHED to the end of this response
        renderAttachedResponseSuggestions(assistantMsgEl, query, store.getState());
      },
      wordDelay: 18
    });
  }

  function scrollToBottom() {
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    if (conversationScroll) {
      conversationScroll.scrollTop = conversationScroll.scrollHeight;
    }
  }

  /**
   * Intelligence Generator: maps queries to rich, structured editorial blocks
   */
  function generateStructuredAIResponse(query, state) {
    const q = query.toLowerCase();
    const city = CITIES.find(c => c.id === state.selectedCity) || CITIES[0];
    const role = CAREER_ROLES[state.selectedRole] || CAREER_ROLES['data-engineer'];

    // 1. DATA SCIENCE ROADMAP
    if (q.includes('data science') || q.includes('data scientist')) {
      return {
        blocks: [
          {
            type: 'prose',
            text: "Based on current demand across **72,000+ verified Indian tech postings**, the market for **Data Science** in 2026 has matured into production-grade ML engineering rather than exploratory notebook modeling."
          },
          {
            type: 'heading',
            level: 3,
            text: "Core Production Competencies"
          },
          {
            type: 'list',
            ordered: false,
            items: [
              "**Python & Vector Pipelines**: NumPy, PyTorch, LangChain, and embedding store indexing",
              "**SQL & Data Architecture**: Complex window functions, query execution planning, and dbt pipelines",
              "**Empirical Statistics**: Hypothesis testing, Tukey IQR outlier removal, and A/B test power analysis",
              "**Inference Serving**: FastAPI endpoints, Docker containerization, and latency profiling"
            ]
          },
          {
            type: 'callout',
            calloutType: 'skill_unlock',
            data: {
              tag: 'Skill Unlock',
              badge: 'High Impact',
              skill: 'Docker & Microservice Deployment',
              jobs: '+8 matching product roles',
              uplift: '+₹3.2L potential salary uplift',
              description: 'Deploying model endpoints behind containers is currently the #1 differentiator in tier-1 product shortlists.'
            }
          },
          {
            type: 'prose',
            text: "Candidates who bridge statistical modeling with containerized deployments command a **+42% faster interview-to-offer velocity** across Bengaluru and Hyderabad."
          },
          {
            type: 'callout',
            calloutType: 'recommendation',
            data: {
              title: 'Recommended 2026 Focus',
              text: 'Skip generic certification courses. Prioritize shipping **2 live, instrumented inference services** on AWS or GCP with demonstrable latency metrics.'
            }
          },
          {
            type: 'prose',
            text: "Would you like a personalized 3-month prerequisite roadmap or a role comparison with Data Engineering?"
          }
        ],
        followups: [
          "Show 3-month learning plan",
          "Compare with Data Engineer",
          "Suggest portfolio projects"
        ]
      };
    }

    // 2. SDE vs DATA ANALYST SALARY COMPARISON
    if (q.includes('sde') || q.includes('data analyst') || q.includes('compare') || q.includes('salary') || q.includes('salaries')) {
      return {
        blocks: [
          {
            type: 'prose',
            text: `Here is the empirical compensation comparison across **72,000+ Indian job postings** in **${city.name}** for early-to-mid career professionals:`
          },
          {
            type: 'table',
            headers: ['Role & Specialization', 'Median CTC (P50)', 'Top 75th (P75)', 'AI Task Automation Exposure'],
            rows: [
              ['**SDE (Mid-Level)**', '**₹18.5L LPA**', '₹24.0L LPA', '[38% Task-Shielded]'],
              ['**Data Analyst**', '**₹12.0L LPA**', '₹16.5L LPA', '[54% Moderate Exposure]'],
              ['**Data Engineer**', '**₹18.0L LPA**', '₹22.5L LPA', '[32% High Shield]']
            ]
          },
          {
            type: 'callout',
            calloutType: 'insight',
            data: {
              title: 'Market Signal',
              text: `Adding Data Engineering capabilities (Airflow & PySpark) to an Analyst stack increases compensation leverage by [+₹4.2L LPA].`
            }
          },
          {
            type: 'prose',
            text: `The key differentiator in 2026 is distributed systems leverage: pure dashboarding roles are experiencing salary compression, while engineers managing end-to-end data pipelines command top-tier compensation bands.`
          },
          {
            type: 'callout',
            calloutType: 'recommendation',
            data: {
              title: 'Transition Strategy',
              text: 'If currently in an Analyst role, bridge into Data Engineering by mastering **PySpark & dbt** rather than traditional BI reporting tools.'
            }
          }
        ],
        followups: [
          "How to transition from Analyst to SDE",
          "Show Pune vs Bengaluru difference",
          "Salary negotiation scripts"
        ]
      };
    }

    // 3. IS BCA WORTH IT IN 2026?
    if (q.includes('bca') || q.includes('degree') || q.includes('worth it') || q.includes('btech')) {
      return {
        blocks: [
          {
            type: 'prose',
            text: "In 2026, Indian tech hiring has bifurcated between credential-heavy legacy IT services and proof-of-work product firms:"
          },
          {
            type: 'list',
            ordered: false,
            items: [
              "**Product Companies & Startups (Razorpay, Swiggy, Zepto)**: 68% of venture-backed firms have removed mandatory B.Tech filters, evaluating candidates strictly on live deployed GitHub repositories and problem-solving. Starting CTC: **₹8.0L – ₹14.0L LPA**.",
              "**Traditional IT Services (TCS, Infosys, Wipro)**: Maintain rigid degree banding. BCA graduates are routed into entry packages of **₹2.8L – ₹3.4L LPA** with long-term promotion caps without an MCA."
            ]
          },
          {
            type: 'callout',
            calloutType: 'warning',
            data: {
              title: 'Campus Placement Trap',
              text: 'Mass campus recruitment drives for BCA graduates enforce legacy salary ceilings. Direct off-campus product pipelines yield **2.5x to 3.5x higher starting compensation**.'
            }
          },
          {
            type: 'prose',
            text: "If you are pursuing a BCA, your highest-leverage strategy is bypassing campus service drives and shipping **3 production-grade, containerized applications** directly on AWS with verified GitHub commit velocity."
          },
          {
            type: 'callout',
            calloutType: 'recommendation',
            data: {
              title: 'Actionable Advice',
              text: 'An MCA is only required if targeting service firm government contracts. For modern product engineering, a strong proof-of-work portfolio consistently beats an MCA.'
            }
          }
        ],
        followups: [
          "Show high-converting projects for BCA",
          "Is MCA worth doing after BCA?",
          "How to get first off-campus shortlist"
        ]
      };
    }

    // 4. PRODUCT MANAGER ROADMAP
    if (q.includes('product manager') || q.includes('pm') || q.includes('apm')) {
      return {
        blocks: [
          {
            type: 'prose',
            text: "Transitioning into Product Management in India requires demonstrable metrics execution over generalist theory. In 2026, tech firms demand PMs who understand unit economics and technical architecture."
          },
          {
            type: 'heading',
            level: 3,
            text: "High-Priority Evaluation Filters"
          },
          {
            type: 'list',
            ordered: false,
            items: [
              "**Product Analytics**: SQL mastery, conversion funnels, and cohort retention modeling",
              "**Execution & PRDs**: Specifying clean API contracts, sizing engineering complexity, and sprint management",
              "**AI Product UX**: LLM guardrails, hallucination mitigation, latency budgets, and prompt caching"
            ]
          },
          {
            type: 'callout',
            calloutType: 'recommendation',
            data: {
              title: 'High-Converting Portfolio Asset',
              text: 'Build a rigorous teardown of a broken Indian tier-2 UX flow (e.g. Meesho checkout or PhonePe soundbox merchant reconciliation) with proposed metric uplift.'
            }
          },
          {
            type: 'prose',
            text: "Candidates who present quantitative business case studies rather than generic slide decks see a **3x higher callback rate** in Indian APM programs."
          }
        ],
        followups: [
          "Show Indian APM programs",
          "Transition from Developer to PM",
          "Sample PM case study assignment"
        ]
      };
    }

    // 5. PUNE VS BENGALURU
    if (q.includes('pune') || q.includes('bengaluru') || q.includes('cost of living') || q.includes('living cost')) {
      return {
        blocks: [
          {
            type: 'prose',
            text: "Here is the empirical compensation and living cost comparison between **Bengaluru** and **Pune** for a 2–4 YOE tech professional:"
          },
          {
            type: 'table',
            headers: ['Metric', 'Bengaluru', 'Pune', 'Variance'],
            rows: [
              ['**Median CTC (Tukey P50)**', '**₹18.0L LPA**', '**₹15.5L LPA**', '-13.9% in Pune'],
              ['**Active Tech Postings**', '28,400+ roles', '11,800+ roles', '2.4x higher in BLR'],
              ['**Avg 2BHK Rent (Tech Corridors)**', '₹28,000 / mo', '₹18,500 / mo', '34% lower in Pune'],
              ['**Effective Net Savings**', '₹52,000 / mo', '₹56,500 / mo', '+8.6% in Pune']
            ]
          },
          {
            type: 'callout',
            calloutType: 'insight',
            data: {
              title: 'Disposable Income Equivalence',
              text: 'Due to housing and commute differences, **₹16.0L in Pune** yields the exact same monthly disposable savings as **₹18.5L in Bengaluru**.'
            }
          },
          {
            type: 'prose',
            text: "**Strategic Guidance**: Choose Pune for lower daily friction and higher initial savings; choose Bengaluru if your immediate priority is maximizing switching velocity and multi-offer leverage."
          }
        ],
        followups: [
          "Compare Hyderabad vs Bengaluru",
          "What about remote Indian roles?",
          "How to negotiate relocation bonus"
        ]
      };
    }

    // 6. PYTHON / CODE / SCRIPT / TUKEY IQR
    if (q.includes('python') || q.includes('code') || q.includes('script') || q.includes('iqr') || q.includes('tukey') || q.includes('algorithm')) {
      return {
        blocks: [
          {
            type: 'prose',
            text: "Here is the production implementation of the **Tukey IQR Outlier Truncation** algorithm used by Vriddhi to calculate market compensation medians:"
          },
          {
            type: 'code',
            language: 'python',
            code: `import numpy as np

def calculate_tukey_iqr_benchmark(salaries_lpa):
    """
    Filters unrepresentative high/low postings and computes
    interquartile ranges for verified compensation bands.
    """
    clean_data = np.array(salaries_lpa)
    p25, p75 = np.percentile(clean_data, [25, 75])
    iqr = p75 - p25
    
    # Tukey bounds (1.5x IQR)
    lower_bound = p25 - (1.5 * iqr)
    upper_bound = p75 + (1.5 * iqr)
    filtered = clean_data[(clean_data >= lower_bound) & (clean_data <= upper_bound)]
    
    return {
        "p25": round(float(p25), 1),
        "median_p50": round(float(np.median(filtered)), 1),
        "p75": round(float(p75), 1),
        "iqr_spread": round(float(iqr), 1),
        "sample_size": len(filtered)
    }`
          },
          {
            type: 'callout',
            calloutType: 'insight',
            data: {
              title: 'Methodology Insight',
              text: 'Tukey IQR prevents single unverified CTC outliers (e.g. ₹60L international remote posts) from distorting median salary projections.'
            }
          },
          {
            type: 'prose',
            text: "You can plug your target role's salary distribution into this function to determine fair counter-offer brackets during negotiations."
          }
        ],
        followups: [
          "Explain salary negotiation scripts",
          "How does Vriddhi scrape postings?",
          "Show 3-month learning plan"
        ]
      };
    }

    // 7. 3-MONTH LEARNING PLAN
    if (q.includes('3-month') || q.includes('learning plan') || q.includes('roadmap') || q.includes('plan')) {
      const topSkill = role.top_skills[0]?.name || 'Apache Spark';
      return {
        blocks: [
          {
            type: 'prose',
            text: `Here is an individualized **3-Month High-ROI Sprint** for **${role.title}** designed to unlock tier-1 product shortlists in **${city.name}**:`
          },
          {
            type: 'heading',
            level: 3,
            text: "Month-by-Month Execution Architecture"
          },
          {
            type: 'list',
            ordered: true,
            items: [
              `**Month 1: Pipeline Hardening**: Deepen SQL window functions, distributed query tuning, and transactional consistency.`,
              `**Month 2: High-ROI Unlock (${topSkill})**: Build a production streaming pipeline ingesting 10k events/sec with automated schema migration.`,
              `**Month 3: Containerization & Cloud Deployment**: Package systems using Docker & Kubernetes on AWS; publish a detailed technical architecture post.`
            ]
          },
          {
            type: 'callout',
            calloutType: 'skill_unlock',
            data: {
              tag: 'Milestone Unlock',
              badge: 'Highest ROI',
              skill: topSkill,
              jobs: '+6 additional matching jobs',
              uplift: '+₹2.8L potential salary uplift',
              description: 'Completing this 3-month sprint moves your profile readiness from **68%** to **88%**.'
            }
          },
          {
            type: 'prose',
            text: "Would you like recommended open-source repository templates or interview system-design counter-scripts?"
          }
        ],
        followups: [
          "Suggest repository templates",
          "How to negotiate for ₹25 LPA",
          "Compare with other roles"
        ]
      };
    }

    // 8. DEFAULT EMPIRICAL FALLBACK BASED ON ACTIVE ROLE & METRO (Exact match to Prompt Section 25)
    const topSkill = role.top_skills[0]?.name || 'Apache Spark';
    return {
      blocks: [
        {
          type: 'prose',
          text: `Based on **72,000+ verified Indian tech postings**, the **${city.name}** market currently shows strong demand for **${role.title}** roles. The median market salary is **₹${role.baseline_salary.p50}L LPA** with a 75th percentile around **₹${role.baseline_salary.max}L LPA**.`
        },
        {
          type: 'callout',
          calloutType: 'skill_unlock',
          data: {
            tag: 'Skill Unlock',
            badge: 'High ROI',
            skill: topSkill,
            jobs: '+6 matching jobs',
            uplift: '+₹2.8L potential salary uplift',
            description: `Adding ${topSkill} provides the highest compensation unlock in the current hiring cycle.`
          }
        },
        {
          type: 'prose',
          text: `Adding **${topSkill}** would therefore be the highest-ROI next step for unlocking tier-1 product firm shortlists. Candidates with verified ${topSkill} experience see a **+38% higher interview callback velocity** in ${city.name}.`
        },
        {
          type: 'callout',
          calloutType: 'insight',
          data: {
            title: 'Market Signal',
            text: `5-year projected growth for this specialization is **+${role.growth_score}% by 2030**, with automation vulnerability estimated at **${role.ai_exposure_score}% (Task-Shielded)**.`
          }
        },
        {
          type: 'prose',
          text: "Would you like specific interview negotiation counter-scripts or an individualized 3-month prerequisite roadmap?"
        }
      ],
      followups: [
        "Show 3-month learning plan",
        "How do I reach ₹25 LPA?",
        "Compare with other roles"
      ]
    };
  }
}

