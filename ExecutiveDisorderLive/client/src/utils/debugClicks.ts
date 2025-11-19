/**
 * Debug Click Handler
 * Paste this in browser console to debug click interactions:
 * 
 * document.addEventListener('click', e => {
 *   const el = document.elementFromPoint(e.clientX, e.clientY);
 *   console.log('🎯 Clicked:', el, 'z-index:', getComputedStyle(el).zIndex);
 * }, true);
 */

export function enableClickDebug() {
  document.addEventListener('click', (e) => {
    const el = document.elementFromPoint(e.clientX, e.clientY);
    const styles = getComputedStyle(el!);
    console.log('🎯 Click Debug:', {
      element: el,
      tagName: el?.tagName,
      className: (el as HTMLElement)?.className,
      zIndex: styles.zIndex,
      pointerEvents: styles.pointerEvents,
      position: styles.position,
    });
  }, true);
  console.log('✅ Click debugging enabled');
}

export function clearServiceWorker() {
  navigator.serviceWorker?.getRegistrations().then(rs => 
    rs.forEach(r => r.unregister())
  );
  caches?.keys().then(ks => 
    ks.forEach(k => caches.delete(k))
  );
  console.log('✅ Service worker cleared');
  setTimeout(() => location.reload(), 100);
}

// Auto-enable in development
if (import.meta.env.DEV) {
  (window as any).debugClicks = enableClickDebug;
  (window as any).clearSW = clearServiceWorker;
  console.log('💡 Debug utils available: debugClicks(), clearSW()');
}
