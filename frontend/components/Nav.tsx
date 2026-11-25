
"use client";

import Link from "next/link";
import { Suspense } from "react";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/resume", label: "Resume" },
  { href: "/practice", label: "Practice" },
  { href: "/history", label: "History" },
  { href: "/profile", label: "Profile" },
  { href: "/settings", label: "Settings" },
];

function NavContent() {
  const pathname = usePathname();

  return (
    <header className="border-b bg-white">
      <nav
        className="mx-auto flex max-w-3xl flex-wrap items-center gap-4 p-4"
        aria-label="Main"
      >
        <span className="font-semibold">Prep Suzy</span>

        {links.map((l) => {
          const active =
            l.href === "/"
              ? pathname === "/"
              : pathname.startsWith(l.href);

          return (
            <Link
              key={l.href}
              href={l.href}
              aria-current={active ? "page" : undefined}
              className={
                active
                  ? "font-medium underline"
                  : "text-gray-600 hover:text-black"
              }
            >
              {l.label}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}

export default function Nav() {
  return (
    <Suspense fallback={null}>
      <NavContent />
    </Suspense>
  );
}
