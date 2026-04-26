/**
 * AcademiX — utils.js
 * Funciones reutilizables en todo el frontend.
 */

/* — Keyframe del toast inyectado una sola vez — */
const _toastStyle = document.createElement('style');
_toastStyle.textContent = `
  @keyframes slideIn  { from { transform: translateY(12px); opacity: 0; } }
  @keyframes slideOut { to   { transform: translateY(12px); opacity: 0; } }
`;
document.head.appendChild(_toastStyle);

/* ─────────────────────────────────────────
   FECHAS
───────────────────────────────────────── */

/* Formato de fecha legible: "25 abr. 2026" */
export function formatDate(isoString) {
  if (!isoString) return '—';
  return new Date(isoString).toLocaleDateString('es-CO', {
    day: '2-digit', month: 'short', year: 'numeric',
  });
}

/* Tiempo relativo: "Hace 3 horas" */
export function timeAgo(isoString) {
  const diff  = Date.now() - new Date(isoString).getTime();
  const mins  = Math.floor(diff / 60_000);
  const hours = Math.floor(diff / 3_600_000);
  const days  = Math.floor(diff / 86_400_000);

  if (mins  < 1)  return 'Justo ahora';
  if (mins  < 60) return `Hace ${mins} min`;
  if (hours < 24) return `Hace ${hours} hora${hours > 1 ? 's' : ''}`;
  return `Hace ${days} día${days > 1 ? 's' : ''}`;
}

/* ─────────────────────────────────────────
   AVATARES
───────────────────────────────────────── */

/* Dos iniciales en mayúscula: "María López" → "ML" */
export function getInitials(name = '') {
  return name.trim().split(' ')
    .slice(0, 2)
    .map(w => w[0]?.toUpperCase() || '')
    .join('');
}

/* Color de avatar determinista según el nombre */
const AVATAR_COLORS = [
  '#1a56db', '#0ea5e9', '#10b981',
  '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899',
];

export function avatarColor(name = '') {
  const code = [...name].reduce((acc, c) => acc + c.charCodeAt(0), 0);
  return AVATAR_COLORS[code % AVATAR_COLORS.length];
}

/* ─────────────────────────────────────────
   NOTIFICACIONES TOAST
───────────────────────────────────────── */

const TOAST_CONFIG = {
  success: { bg: '#10b981', icon: '✓' },
  error:   { bg: '#ef4444', icon: '✕' },
  warning: { bg: '#f59e0b', icon: '!' },
  info:    { bg: '#3b82f6', icon: 'i' },
};

export function showToast(message, type = 'success', duration = 3000) {
  /* Eliminar toast previo si existe */
  document.querySelector('.toast')?.remove();

  const { bg, icon } = TOAST_CONFIG[type] ?? TOAST_CONFIG.info;

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<span>${icon}</span> ${message}`;
  toast.style.cssText = `
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 9999;
    background: ${bg};
    color: #fff;
    padding: 12px 20px;
    border-radius: 10px;
    font-family: var(--font-sans);
    font-size: 13.5px;
    font-weight: 500;
    box-shadow: 0 4px 16px rgba(0,0,0,.15);
    display: flex;
    align-items: center;
    gap: 8px;
    animation: slideIn .2s ease forwards;
  `;

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'slideOut .2s ease forwards';
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
  }, duration);
}

/* ─────────────────────────────────────────
   CONFIRMACIÓN
───────────────────────────────────────── */

/* Renombrado para no colisionar con window.confirm */
export function confirmAction(message) {
  return window.confirm(message);
}

/* ─────────────────────────────────────────
   UTILIDADES GENERALES
───────────────────────────────────────── */

/* Truncar texto largo */
export function truncate(text = '', maxLength = 60) {
  return text.length > maxLength ? text.slice(0, maxLength).trimEnd() + '…' : text;
}

/* Capitalizar primera letra */
export function capitalize(text = '') {
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

/* Formatear número con separador de miles */
export function formatNumber(n) {
  return Number(n).toLocaleString('es-CO');
}

/* Debounce — útil para buscadores en tiempo real */
export function debounce(fn, delay = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}