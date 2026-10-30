// RecycleTrace - Tracking & Timeline Visualizer

const Tracking = {
  renderTimeline(containerId, events) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    if (!events || events.length === 0) {
      container.innerHTML = '<p style="text-align:center; padding:1.5rem; color:#94a3b8;">No events recorded yet.</p>';
      return;
    }

    events.forEach(evt => {
      const item = document.createElement('div');
      item.className = 'timeline-item';
      const isVerified = evt.event_type === 'verification_approved';
      const isRejected = ['verification_rejected', 'rejected', 'collection_failed'].includes(evt.event_type);

      let icon = '•';
      if (isVerified) icon = '✓';
      else if (isRejected) icon = '✕';

      item.innerHTML = `
        <div class="timeline-marker ${isVerified ? 'verified' : ''} ${isRejected ? 'rejected' : ''}">
          ${icon}
        </div>
        <div class="timeline-content">
          <div class="timeline-header">
            <span class="timeline-title">${(evt.event_type || '').replace(/_/g, ' ')}</span>
            <span class="timeline-date">${formatDate(evt.timestamp)}</span>
          </div>
          <div style="font-size:0.8125rem; color:#64748b; margin-top:0.25rem;">
            Actor: <strong>${(evt.actor_role || '').replace(/_/g, ' ')}</strong>
            ${evt.weight_kg ? ` · Weight: <strong>${formatWeight(evt.weight_kg)}</strong>` : ''}
          </div>
          ${evt.notes ? `<p style="font-size:0.85rem; margin-top:0.5rem; color:#334155;">${evt.notes}</p>` : ''}
        </div>
      `;
      container.appendChild(item);
    });
  }
};

window.Tracking = Tracking;

