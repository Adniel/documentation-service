/**
 * Print utility — triggers browser print dialog with proper styling.
 *
 * Sprint I: Context Menu
 */

export function triggerPrint() {
  document.body.classList.add('print-mode');
  window.print();
  // Remove after print dialog closes
  const cleanup = () => {
    document.body.classList.remove('print-mode');
    window.removeEventListener('afterprint', cleanup);
  };
  window.addEventListener('afterprint', cleanup);
  // Fallback timeout in case afterprint doesn't fire
  setTimeout(cleanup, 3000);
}
