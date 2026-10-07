/**
 * VRIDDHI (वृद्धि) — Reactive State Store
 * Centralized state for views, filters, candidate selections, and counselor.
 */

class VriddhiStore {
  constructor() {
    this.state = {
      currentView: 'overview', // 'overview' | 'career-intel' | 'skill-gap' | 'job-salary'
      selectedCity: 'bengaluru',
      selectedRole: 'data-engineer',
      selectedCandidate: 'aarav-mehta',
      weeklyStudyHours: 15,
      jobFilterMode: 'all',
      aiDrawerOpen: false,
      chatMessages: [
        {
          role: 'assistant',
          content: `Namaste! I am the **Vriddhi AI Career Counselor**, grounded in empirical workforce data across **72,000+ Indian tech records** and **5 tech metros**.\n\nWhether you need to benchmark your compensation against city percentiles, diagnose skill gaps blocking interview calls, or simulate the salary impact of learning new technologies like Docker or PySpark, I'm here to provide verifiable strategic guidance.\n\n*Select a prompt below or ask your own question.*`
        }
      ]
    };
    this.listeners = [];
  }

  getState() {
    return this.state;
  }

  setState(updates) {
    this.state = { ...this.state, ...updates };
    this.notify();
  }

  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  notify() {
    this.listeners.forEach(listener => listener(this.state));
  }
}

export const store = new VriddhiStore();
