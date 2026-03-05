"use client";

/**
 * Dashboard sidebar navigation with mobile responsive overlay.
 */

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/documents", label: "Documents" },
  { href: "/analysis", label: "Analysis" },
  { href: "/analysis/new", label: "New Analysis" },
];

interface SidebarProps {
  /** Whether the mobile sidebar is open. */
  isOpen: boolean;
  /** Callback to close the mobile sidebar. */
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  const navContent = (
    <nav className="flex flex-col gap-1">
      {NAV_ITEMS.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          onClick={onClose}
          className={cn(
            "rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent",
            pathname === item.href
              ? "bg-accent text-accent-foreground"
              : "text-muted-foreground",
          )}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden w-56 border-r bg-muted/40 p-4 md:block">
        {navContent}
      </aside>

      {/* Mobile overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={onClose}
            aria-hidden="true"
          />
          <aside className="absolute left-0 top-0 h-full w-56 bg-background p-4 shadow-lg">
            {navContent}
          </aside>
        </div>
      )}
    </>
  );
}
