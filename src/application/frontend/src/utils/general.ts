import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function pathname_equal(a: string, b: string) {
  const norm = (s: string) => (s.endsWith('/') ? s.slice(0, -1) : s);
  return norm(a) === norm(b);
}
