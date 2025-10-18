import { useMemo, useState } from "react";
import clsx from "clsx";

export interface CommandItem {
  id: string;
  label: string;
  shortcut?: string;
  onSelect: () => void;
}

export interface CommandMenuProps {
  items: CommandItem[];
  placeholder?: string;
  emptyState?: string;
}

export function CommandMenu({
  items,
  placeholder = "Type a command",
  emptyState = "No results"
}: CommandMenuProps) {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const lower = query.toLowerCase();
    return items.filter((item) => item.label.toLowerCase().includes(lower));
  }, [items, query]);

  return (
    <div
      className={clsx(
        "w-full max-w-lg rounded-xl border border-[var(--ui-border)] bg-[var(--ui-surface-alt)] shadow-lg"
      )}
    >
      <input
        className="w-full border-b border-[var(--ui-border)] bg-transparent px-4 py-3 text-sm text-[var(--ui-text)] focus:outline-none"
        placeholder={placeholder}
        value={query}
        onChange={(event) => setQuery(event.target.value)}
      />
      <ul className="max-h-64 overflow-y-auto py-2">
        {filtered.length === 0 ? (
          <li className="px-4 py-3 text-sm text-[var(--ui-text-muted)]">{emptyState}</li>
        ) : (
          filtered.map((item) => (
            <li
              key={item.id}
              className="flex cursor-pointer items-center justify-between px-4 py-2 text-sm text-[var(--ui-text)] hover:bg-[var(--ui-surface)]"
              onClick={item.onSelect}
            >
              <span>{item.label}</span>
              {item.shortcut ? (
                <kbd className="text-xs text-[var(--ui-text-muted)]">{item.shortcut}</kbd>
              ) : null}
            </li>
          ))
        )}
      </ul>
    </div>
  );
}
