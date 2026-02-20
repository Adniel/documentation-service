/**
 * Skip navigation links for keyboard/screen reader accessibility.
 * Visually hidden, becomes visible on Tab focus.
 *
 * Sprint I: WCAG 2.1 AA
 */

export function SkipLinks() {
  return (
    <div className="fixed top-0 left-0 z-[100]">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-[100] focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-md focus:shadow-lg focus:outline-none"
      >
        Skip to content
      </a>
      <a
        href="#main-nav"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-40 focus:z-[100] focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-md focus:shadow-lg focus:outline-none"
      >
        Skip to navigation
      </a>
    </div>
  );
}
