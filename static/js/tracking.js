// RecycleTrace - Tracking, Timeline & Verification Visualizer

const Tracking = {
  renderTimeline(containerId, events) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    if (!events || events.length === 0) {
      container.innerHTML = '<p style="text-align:center; padding:2rem; color:#94a3b8;">No custody events recorded yet.</p>';
      return;
    }

    events.forEach((evt, idx) => {
      const item = document.createElement('div');
      item.className = 'timeline-item';
      item.style.animationDelay = `${idx * 120}ms`;

      const isVerified = evt.event_type === 'verification_approved';
      const isRejected = ['verification_rejected', 'rejected', 'collection_failed'].includes(evt.event_type);
      const isLatest = idx === events.length - 1;

      let icon = '•';
      if (isVerified) icon = '✓';
      else if (isRejected) icon = '✕';
      else if (evt.event_type === 'registered') icon = '📦';
      else if (evt.event_type === 'collected') icon = '🚛';
      else if (evt.event_type === 'in_transit') icon = '🔄';
      else if (evt.event_type === 'received') icon = '🏭';
      else if (evt.event_type === 'processed') icon = '⚙️';

      let markerClass = '';
      if (isVerified) markerClass = 'verified';
      else if (isRejected) markerClass = 'rejected';

      item.innerHTML = `
        <div class="timeline-marker ${markerClass}">
          ${icon}
        </div>
        <div class="timeline-content">
          <div class="timeline-header">
            <span class="timeline-title">${(evt.event_type || '').replace(/_/g, ' ')}</span>
            <span class="timeline-date">${formatDate(evt.timestamp)}</span>
          </div>
          <div style="font-size:0.8125rem; color:#64748b; margin-top:0.35rem; display:flex; flex-wrap:wrap; gap:0.75rem;">
            <span>Actor: <strong>${(evt.actor_role || '').replace(/_/g, ' ')}</strong></span>
            ${evt.weight_kg ? `<span>· Recorded: <strong style="color:#0f172a;">${formatWeight(evt.weight_kg)}</strong></span>` : ''}
          </div>
          ${evt.notes ? `<p style="font-size:0.875rem; margin-top:0.6rem; color:#334155; background:#f8fafc; padding:0.6rem 0.85rem; border-radius:6px; border-left:3px solid #cbd5e1;">${evt.notes}</p>` : ''}
        </div>
      `;
      container.appendChild(item);
    });
  },

  /**
   * Confetti celebration for verified recycled batches
   */
  celebrateVerification() {
    const count = 35;
    const colors = ['#10b981', '#22c55e', '#3b82f6', '#f59e0b', '#059669', '#34d399'];
    
    for (let i = 0; i < count; i++) {
      const particle = document.createElement('div');
      particle.className = 'celebration-sparkle';
      
      const size = Math.random() * 8 + 5;
      const left = Math.random() * 100;
      const animDuration = Math.random() * 2 + 1.8;
      const color = colors[Math.floor(Math.random() * colors.length)];
      
      particle.style.cssText = `
        position: fixed;
        bottom: 0;
        left: ${left}vw;
        width: ${size}px;
        height: ${size * (Math.random() > 0.5 ? 1 : 1.6)}px;
        background-color: ${color};
        border-radius: ${Math.random() > 0.5 ? '50%' : '2px'};
        z-index: 10000;
        pointer-events: none;
        opacity: 0.9;
        transform: translateY(0) rotate(0deg);
        animation: flyUp ${animDuration}s cubic-bezier(0.25, 1, 0.5, 1) forwards;
      `;
      
      document.body.appendChild(particle);
      setTimeout(() => particle.remove(), animDuration * 1000);
    }
  }
};

// Add flyUp keyframe if not present
if (!document.getElementById('tracking-anim-style')) {
  const style = document.createElement('style');
  style.id = 'tracking-anim-style';
  style.textContent = `
    @keyframes flyUp {
      0% {
        transform: translateY(0) rotate(0deg);
        opacity: 1;
      }
      80% {
        opacity: 0.8;
      }
      100% {
        transform: translateY(-90vh) rotate(${Math.random() > 0.5 ? 400 : -400}deg);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(style);
}

window.Tracking = Tracking;
