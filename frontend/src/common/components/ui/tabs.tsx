/**
 * Tabs component.
 *
 * A set of layered sections of content—known as tab panels—that are displayed one at a time.
 */

import * as React from 'react';
import { cn } from '@/common/utils/cn';

interface TabsProps {
  children: React.ReactNode;
  value?: string;
  onValueChange?: (value: string) => void;
  className?: string;
}

interface TabsListProps {
  children: React.ReactNode;
  className?: string;
}

interface TabsTriggerProps {
  children: React.ReactNode;
  value: string;
  disabled?: boolean;
  className?: string;
}

interface TabsContentProps {
  children: React.ReactNode;
  value: string;
  className?: string;
}

const TabsContext = React.createContext<{
  value: string;
  onValueChange: (value: string) => void;
} | null>(null);

export function Tabs({ children, value, onValueChange, className = '' }: TabsProps) {
  const [internalValue, setInternalValue] = React.useState(value ?? '');
  const currentValue = value ?? internalValue;
  const handleChange = onValueChange ?? setInternalValue;

  return (
    <TabsContext.Provider value={{ value: currentValue, onValueChange: handleChange }}>
      <div className={className}>{children}</div>
    </TabsContext.Provider>
  );
}

export function TabsList({ children, className = '' }: TabsListProps) {
  return (
    <div
      role="tablist"
      className={cn(
        'inline-flex h-10 items-center justify-center rounded-md bg-muted p-1',
        className
      )}
    >
      {children}
    </div>
  );
}

export function TabsTrigger({ children, value, disabled = false, className = '' }: TabsTriggerProps) {
  const context = React.useContext(TabsContext);
  if (!context) throw new Error('TabsTrigger must be used within Tabs');

  const isActive = context.value === value;

  return (
    <button
      role="tab"
      aria-selected={isActive}
      disabled={disabled}
      onClick={() => !disabled && context.onValueChange(value)}
      className={cn(
        'inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5',
        'text-sm font-medium ring-offset-background transition-all',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
        'disabled:pointer-events-none disabled:opacity-50',
        isActive
          ? 'bg-background text-foreground shadow-sm'
          : 'text-muted-foreground hover:text-foreground',
        className
      )}
    >
      {children}
    </button>
  );
}

export function TabsContent({ children, value, className = '' }: TabsContentProps) {
  const context = React.useContext(TabsContext);
  if (!context) throw new Error('TabsContent must be used within Tabs');

  if (context.value !== value) return null;

  return (
    <div
      role="tabpanel"
      className={cn('mt-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring', className)}
    >
      {children}
    </div>
  );
}