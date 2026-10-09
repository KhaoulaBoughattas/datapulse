"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/pipelines", label: "Pipelines" },
  { href: "/data-sources", label: "Data Sources" },
  { href: "/datasets", label: "Datasets" },
  { href: "/data-quality", label: "Data Quality" },
  { href: "/lineage", label: "Lineage" },
  { href: "/monitoring", label: "Monitoring" },
  { href: "/settings", label: "Settings" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="w-56 shrink-0 bg-white border-r border-slate-200 flex flex-col h-screen sticky top-0">
      <div className="px-5 py-5 border-b border-slate-100">
        <span className="text-lg font-semibold text-brand-600">DataPulse</span>
      </div>
      <nav className="flex-1 px-2 py-4 space-y-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href;
          return (
            <Link key={item.href} href={item.href} className={`block px-3 py-2 rounded-md text-sm font-medium ${active ? "bg-brand-50 text-brand-700" : "text-slate-600 hover:bg-slate-100"}`}>
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="px-4 py-4 border-t border-slate-100 text-xs text-slate-500">
        <div className="mb-1">{user?.email}</div>
        <div className="mb-3 inline-block px-2 py-0.5 rounded bg-slate-100 text-slate-600">{user?.role}</div>
        <button onClick={logout} className="block text-red-600 hover:underline">Sign out</button>
      </div>
    </aside>
  );
}
