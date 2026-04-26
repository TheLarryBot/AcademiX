/**
 * AcademiX — sidebar.js
 * Marca automáticamente el ítem activo del sidebar
 * según la URL actual. Incluir en todas las páginas.
 */

document.addEventListener('DOMContentLoaded', () => {
  const items   = document.querySelectorAll('.sidebar-item[data-page]');
  const current = window.location.pathname;

  // Extraer el segmento de ruta real: "/nueva-actividad" → "nueva-actividad"
  const segment = current.replace(/^\/+|\/+$/g, '');

  items.forEach(item => {
    item.classList.remove('active');                     // limpiar primero
    const page = item.getAttribute('data-page');

    // Comparación exacta para evitar que "actividades" active "nueva-actividad"
    if (segment === page) {
      item.classList.add('active');
    }
  });

  // Marcar dashboard cuando estemos en la raíz "/"
  if (segment === '') {
    document.querySelector('[data-page="dashboard"]')?.classList.add('active');
  }
});

