import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function pathname_equal(a: string, b: string) {
  const norm = (s: string) => (s.endsWith('/') ? s.slice(0, -1) : s);
  return norm(a) === norm(b);
}

export function makeDebouncedLoader(
  fn: (q: string) => Promise<any[]>,
  delay: number
) {
  let timer: NodeJS.Timeout | null = null;
  let pending: (value: any[]) => void;

  return (input: string) =>
    new Promise<any[]>((resolve) => {
      pending = resolve;
      if (timer) clearTimeout(timer);
      timer = setTimeout(async () => {
        const out = await fn(input);
        pending(out);
      }, delay);
    });
}
