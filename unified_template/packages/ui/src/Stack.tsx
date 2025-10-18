import type { PropsWithChildren, HTMLAttributes } from 'react';
import clsx from 'clsx';

export interface StackProps extends HTMLAttributes<HTMLDivElement> {
  gap?: 'xs' | 'sm' | 'md' | 'lg';
  direction?: 'column' | 'row';
}

const GAP_CLASS: Record<NonNullable<StackProps['gap']>, string> = {
  xs: 'gap-1.5',
  sm: 'gap-3',
  md: 'gap-4',
  lg: 'gap-6'
};

export function Stack({ gap = 'md', direction = 'column', className, children, ...props }: PropsWithChildren<StackProps>) {
  return (
    <div className={clsx('flex', direction === 'column' ? 'flex-col' : 'flex-row', GAP_CLASS[gap], className)} {...props}>
      {children}
    </div>
  );
}

