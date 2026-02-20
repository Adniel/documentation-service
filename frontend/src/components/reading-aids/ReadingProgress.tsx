/**
 * Reading progress bar fixed at top of viewport.
 * Throttled via requestAnimationFrame.
 *
 * Sprint I: Reading Aids
 */

import { useEffect, useState, useRef } from 'react';

export function ReadingProgress() {
  const [progress, setProgress] = useState(0);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    const handleScroll = () => {
      if (rafRef.current) return;

      rafRef.current = requestAnimationFrame(() => {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const pct = docHeight > 0 ? Math.min(100, (scrollTop / docHeight) * 100) : 0;
        setProgress(pct);
        rafRef.current = 0;
      });
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', handleScroll);
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, []);

  return (
    <div
      className="reading-progress-bar fixed top-0 left-0 right-0 h-[3px] z-50 bg-transparent"
      aria-hidden="true"
    >
      <div
        className="h-full bg-blue-500 transition-[width] duration-100"
        style={{ width: `${progress}%` }}
      />
    </div>
  );
}
