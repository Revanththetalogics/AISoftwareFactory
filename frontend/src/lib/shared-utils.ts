/**
 * Shared utility functions between frontend and backend.
 * 
 * This module provides common utility functions that maintain consistency
 * between frontend and backend implementations.
 */

/**
 * Format duration in milliseconds to human readable string.
 * Mirrors backend format_duration function.
 * 
 * @param ms - Duration in milliseconds
 * @returns Human readable duration string
 * 
 * @example
 * ```typescript
 * formatDuration(5000) // "5.0s"
 * formatDuration(120000) // "2.0m"
 * formatDuration(3600000) // "1.0h"
 * ```
 */
export function formatDuration(ms: number): string {
  const seconds = ms / 1000;
  
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  } else if (seconds < 3600) {
    const minutes = seconds / 60;
    return `${minutes.toFixed(1)}m`;
  } else if (seconds < 86400) {
    const hours = seconds / 3600;
    return `${hours.toFixed(1)}h`;
  } else {
    const days = seconds / 86400;
    return `${days.toFixed(1)}d`;
  }
}

/**
 * Format bytes to human readable string.
 * Mirrors backend format_bytes function.
 * 
 * @param bytes - Size in bytes
 * @returns Human readable size string
 * 
 * @example
 * ```typescript
 * formatBytes(1024) // "1.0 KB"
 * formatBytes(1048576) // "1.0 MB"
 * formatBytes(1073741824) // "1.0 GB"
 * ```
 */
export function formatBytes(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let value = bytes;
  let unitIndex = 0;
  
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex++;
  }
  
  return `${value.toFixed(1)} ${units[unitIndex]}`;
}

/**
 * Truncate a string to maximum length.
 * Mirrors backend truncate_string function.
 * 
 * @param text - Text to truncate
 * @param maxLength - Maximum length (default: 100)
 * @param suffix - Suffix to add if truncated (default: "...")
 * @returns Truncated string
 * 
 * @example
 * ```typescript
 * truncateString("This is a very long string", 10) // "This is..."
 * truncateString("Short", 10) // "Short"
 * ```
 */
export function truncateString(text: string, maxLength: number = 100, suffix: string = "..."): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength - suffix.length) + suffix;
}

/**
 * Format date to ISO string.
 * Mirrors backend format_datetime function.
 * 
 * @param date - Date to format (can be Date object, string, or null)
 * @returns ISO formatted string or null
 * 
 * @example
 * ```typescript
 * formatDate(new Date()) // "2024-01-15T10:30:00.000Z"
 * formatDate(null) // null
 * ```
 */
export function formatDate(date: Date | string | null): string | null {
  if (date === null || date === undefined) {
    return null;
  }
  
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toISOString();
}

/**
 * Generate a random ID.
 * Mirrors backend generate_id function.
 * 
 * @returns Random UUID string
 * 
 * @example
 * ```typescript
 * generateId() // "550e8400-e29b-41d4-a716-446655440000"
 * ```
 */
export function generateId(): string {
  return crypto.randomUUID();
}

/**
 * Validate email format.
 * Mirrors backend validate_email function.
 * 
 * @param email - Email to validate
 * @returns True if valid email format
 * 
 * @example
 * ```typescript
 * validateEmail("user@example.com") // true
 * validateEmail("invalid-email") // false
 * ```
 */
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate URL format.
 * Mirrors backend validate_url function.
 * 
 * @param url - URL to validate
 * @returns True if valid URL format
 * 
 * @example
 * ```typescript
 * validateUrl("https://example.com") // true
 * validateUrl("invalid-url") // false
 * ```
 */
export function validateUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Debounce function to limit rate of execution.
 * 
 * @param func - Function to debounce
 * @param wait - Wait time in milliseconds
 * @returns Debounced function
 * 
 * @example
 * ```typescript
 * const debouncedSearch = debounce((query) => search(query), 300);
 * ```
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };
    
    if (timeout) {
      clearTimeout(timeout);
    }
    
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttle function to limit rate of execution.
 * 
 * @param func - Function to throttle
 * @param limit - Limit time in milliseconds
 * @returns Throttled function
 * 
 * @example
 * ```typescript
 * const throttledScroll = throttle((event) => handleScroll(event), 100);
 * ```
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false;
  
  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * Sleep function for async operations.
 * 
 * @param ms - Milliseconds to sleep
 * @returns Promise that resolves after specified time
 * 
 * @example
 * ```typescript
 * await sleep(1000); // Waits 1 second
 * ```
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Deep clone an object using structuredClone (modern browsers) or fallback.
 * 
 * @param obj - Object to clone
 * @returns Deep cloned object
 */
export function deepClone<T>(obj: T): T {
  if (typeof structuredClone !== 'undefined') {
    return structuredClone(obj);
  }
  
  // Fallback for older environments
  return JSON.parse(JSON.stringify(obj));
}