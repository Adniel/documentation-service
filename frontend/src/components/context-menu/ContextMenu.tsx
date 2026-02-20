/**
 * Custom right-click context menu for reader content.
 * Positioned at click coordinates, accessible via keyboard.
 *
 * Sprint I: Context Menu
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';

export interface ContextMenuItem {
  label: string;
  icon?: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
  separator?: boolean;
}

interface ContextMenuProps {
  items: ContextMenuItem[];
  containerRef: React.RefObject<HTMLElement | null>;
}

export function ContextMenu({ items, containerRef }: ContextMenuProps) {
  const [visible, setVisible] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [focusIndex, setFocusIndex] = useState(-1);
  const menuRef = useRef<HTMLDivElement>(null);

  const close = useCallback(() => {
    setVisible(false);
    setFocusIndex(-1);
  }, []);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleContextMenu = (e: MouseEvent) => {
      e.preventDefault();
      setPosition({ x: e.clientX, y: e.clientY });
      setVisible(true);
      setFocusIndex(-1);
    };

    container.addEventListener('contextmenu', handleContextMenu);
    return () => container.removeEventListener('contextmenu', handleContextMenu);
  }, [containerRef]);

  useEffect(() => {
    if (!visible) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        close();
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        close();
        return;
      }

      const activeItems = items.filter((i) => !i.separator && !i.disabled);
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setFocusIndex((i) => (i + 1) % activeItems.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setFocusIndex((i) => (i - 1 + activeItems.length) % activeItems.length);
      } else if (e.key === 'Enter' && focusIndex >= 0) {
        e.preventDefault();
        activeItems[focusIndex]?.onClick();
        close();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [visible, close, items, focusIndex]);

  // Adjust position to keep menu within viewport
  useEffect(() => {
    if (!visible || !menuRef.current) return;
    const rect = menuRef.current.getBoundingClientRect();
    const vw = window.innerWidth;
    const vh = window.innerHeight;

    let { x, y } = position;
    if (x + rect.width > vw) x = vw - rect.width - 8;
    if (y + rect.height > vh) y = vh - rect.height - 8;
    if (x !== position.x || y !== position.y) setPosition({ x, y });
  }, [visible, position]);

  if (!visible) return null;

  let activeIdx = 0;

  return createPortal(
    <div
      ref={menuRef}
      className="context-menu fixed z-[70] bg-slate-800 border border-slate-600 rounded-lg shadow-2xl py-1 min-w-[200px]"
      style={{ left: position.x, top: position.y }}
      role="menu"
    >
      {items.map((item, i) => {
        if (item.separator) {
          return <div key={i} className="border-t border-slate-700 my-1" />;
        }

        const currentActiveIdx = activeIdx++;
        const isFocused = currentActiveIdx === focusIndex;

        return (
          <button
            key={i}
            role="menuitem"
            disabled={item.disabled}
            className={`w-full text-left px-3 py-2 text-sm flex items-center gap-2 transition-colors ${
              isFocused
                ? 'bg-slate-700 text-white'
                : item.disabled
                ? 'text-slate-500 cursor-not-allowed'
                : 'text-slate-300 hover:bg-slate-700 hover:text-white'
            }`}
            onClick={() => {
              item.onClick();
              close();
            }}
          >
            {item.icon && <span className="w-4 h-4 flex-shrink-0">{item.icon}</span>}
            {item.label}
          </button>
        );
      })}
    </div>,
    document.body
  );
}
