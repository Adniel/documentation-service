import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ReaderPreferencesState {
  theme: 'dark' | 'light';
  fontSize: number;
  highContrast: boolean;
  dyslexicFont: boolean;
  focusMode: boolean;
  speedReaderWpm: number;
  tocCollapsed: boolean;
  setTheme: (theme: 'dark' | 'light') => void;
  toggleTheme: () => void;
  setFontSize: (size: number) => void;
  increaseFontSize: () => void;
  decreaseFontSize: () => void;
  toggleHighContrast: () => void;
  toggleDyslexicFont: () => void;
  toggleFocusMode: () => void;
  setSpeedReaderWpm: (wpm: number) => void;
  toggleTocCollapsed: () => void;
  resetAll: () => void;
}

const DEFAULTS = {
  theme: 'dark' as const,
  fontSize: 16,
  highContrast: false,
  dyslexicFont: false,
  focusMode: false,
  speedReaderWpm: 300,
  tocCollapsed: false,
};

export const useReaderPreferencesStore = create<ReaderPreferencesState>()(
  persist(
    (set) => ({
      ...DEFAULTS,
      setTheme: (theme) => set({ theme }),
      toggleTheme: () =>
        set((state) => ({ theme: state.theme === 'dark' ? 'light' : 'dark' })),
      setFontSize: (size) =>
        set({ fontSize: Math.min(24, Math.max(14, size)) }),
      increaseFontSize: () =>
        set((state) => ({ fontSize: Math.min(24, state.fontSize + 2) })),
      decreaseFontSize: () =>
        set((state) => ({ fontSize: Math.max(14, state.fontSize - 2) })),
      toggleHighContrast: () =>
        set((state) => ({ highContrast: !state.highContrast })),
      toggleDyslexicFont: () =>
        set((state) => ({ dyslexicFont: !state.dyslexicFont })),
      toggleFocusMode: () =>
        set((state) => ({ focusMode: !state.focusMode })),
      setSpeedReaderWpm: (wpm) =>
        set({ speedReaderWpm: Math.min(800, Math.max(200, wpm)) }),
      toggleTocCollapsed: () =>
        set((state) => ({ tocCollapsed: !state.tocCollapsed })),
      resetAll: () => set(DEFAULTS),
    }),
    {
      name: 'reader-preferences',
      partialize: (state) => ({
        theme: state.theme,
        fontSize: state.fontSize,
        highContrast: state.highContrast,
        dyslexicFont: state.dyslexicFont,
        focusMode: state.focusMode,
        speedReaderWpm: state.speedReaderWpm,
        tocCollapsed: state.tocCollapsed,
      }),
    }
  )
);
