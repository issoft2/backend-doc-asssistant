import { ref, watchEffect } from 'vue';

export type Theme = 'light' | 'dark' | 'system';

export function useTheme() {
  const theme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'dark');

  watchEffect(() => {
    const root = window.document.documentElement;
    const isDark = theme.value === 'dark' || 
      (theme.value === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
    
    root.classList.toggle('dark', isDark);
    localStorage.setItem('theme', theme.value);
  });

  return { theme };
}