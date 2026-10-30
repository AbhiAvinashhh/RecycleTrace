// RecycleTrace - Dashboard Utilities & KPI Helpers

const Dashboard = {
  async fetchOverview() {
    try {
      const res = await fetch('/api/analytics/overview');
      if (!res.ok) throw new Error('Overview fetch failed');
      return await res.json();
    } catch (err) {
      console.error('[Dashboard] Error fetching overview:', err);
      return null;
    }
  },

  async fetchCollections(days = 30) {
    try {
      const res = await fetch(`/api/analytics/collections?days=${days}`);
      if (!res.ok) throw new Error('Collections fetch failed');
      return await res.json();
    } catch (err) {
      console.error('[Dashboard] Error fetching collections:', err);
      return null;
    }
  },

  async fetchFacilities() {
    try {
      const res = await fetch('/api/analytics/facilities');
      if (!res.ok) throw new Error('Facilities fetch failed');
      return await res.json();
    } catch (err) {
      console.error('[Dashboard] Error fetching facilities:', err);
      return null;
    }
  },

  animateCounter(elementId, targetValue, suffix = '') {
    if (typeof window.animateCounter === 'function') {
      window.animateCounter(elementId, targetValue, 750, suffix);
    } else {
      const el = document.getElementById(elementId);
      if (el) el.textContent = targetValue + suffix;
    }
  }
};

window.Dashboard = Dashboard;
