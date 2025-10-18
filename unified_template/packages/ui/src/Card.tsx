import type { PropsWithChildren, HTMLAttributes } from 'react';
import clsx from 'clsx';

export function Card({ className, children, ...props }: PropsWithChildren<HTMLAttributes<HTMLDivElement>>) {
  return (
    <div
      className={clsx(
        'rounded-xl border border-[var(--ui-border)] bg-[var(--ui-surface-alt)] p-4 shadow-sm',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

