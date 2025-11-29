import { describe, expect, it } from '@jest/globals';
import { cn, pathname_equal } from '@/utils/general';

describe('cn utility function', () => {
  it('should merge class names correctly', () => {
    const result = cn('text-red-500', 'bg-blue-500');
    expect(result).toBe('text-red-500 bg-blue-500');
  });

  it('should handle conditional classes', () => {
    const result = cn(
      'base-class',
      true && 'conditional-class',
      false && 'not-included'
    );
    expect(result).toBe('base-class conditional-class');
  });

  it('should merge conflicting Tailwind classes correctly', () => {
    const result = cn('px-2 py-1', 'px-4');
    expect(result).toBe('py-1 px-4');
  });

  it('should handle arrays of classes', () => {
    const result = cn(['class1', 'class2'], 'class3');
    expect(result).toBe('class1 class2 class3');
  });

  it('should handle objects with conditional classes', () => {
    const result = cn({ active: true, disabled: false, 'text-bold': true });
    expect(result).toBe('active text-bold');
  });

  it('should handle empty input', () => {
    const result = cn();
    expect(result).toBe('');
  });

  it('should handle undefined and null values', () => {
    const result = cn('text-sm', undefined, null, 'text-blue-500');
    expect(result).toBe('text-sm text-blue-500');
  });
});

describe('pathname_equal utility function', () => {
  it('should return true for identical pathnames', () => {
    expect(pathname_equal('/home', '/home')).toBe(true);
  });

  it('should return true when comparing pathname with and without trailing slash', () => {
    expect(pathname_equal('/home/', '/home')).toBe(true);
    expect(pathname_equal('/home', '/home/')).toBe(true);
  });

  it('should return true when both pathnames have trailing slashes', () => {
    expect(pathname_equal('/home/', '/home/')).toBe(true);
  });

  it('should return false for different pathnames', () => {
    expect(pathname_equal('/home', '/about')).toBe(false);
  });

  it('should return false for different pathnames even with trailing slashes', () => {
    expect(pathname_equal('/home/', '/about/')).toBe(false);
  });

  it('should handle root path correctly', () => {
    expect(pathname_equal('/', '/')).toBe(true);
  });

  it('should handle nested paths correctly', () => {
    expect(pathname_equal('/users/profile', '/users/profile')).toBe(true);
    expect(pathname_equal('/users/profile/', '/users/profile')).toBe(true);
  });

  it('should handle paths with query strings or hashes as different', () => {
    expect(pathname_equal('/home?query=1', '/home')).toBe(false);
  });

  it('should be case-sensitive', () => {
    expect(pathname_equal('/Home', '/home')).toBe(false);
  });
});
