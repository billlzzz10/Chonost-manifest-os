import type { ButtonHTMLAttributes, PropsWithChildren } from 'react';
import clsx from 'clsx';

const base = 'inline-flex items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors';
const primary = 'bg-[var(--ui-accent)] text-black hover:brightness-110 focus:outline-none focus:ring-2 focus:ring-[var(--ui-accent)]';
const ghost = 'bg-transparent text-[var(--ui-text)] hover:bg-[var(--ui-surface-alt)]';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost';
}

export function Button({ variant = 'primary', className, children, ...props }: PropsWithChildren<ButtonProps>) {
  return (
    <button className={clsx(base, variant === 'primary' ? primary : ghost, className)} {...props}>
      {children}
    </button>
  );
}

