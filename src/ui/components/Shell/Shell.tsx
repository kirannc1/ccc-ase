"use client";

import { Body1, Divider, Tab, TabList } from "@fluentui/react-components";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";

import styles from "./Shell.module.css";

type NavItem = { href: string; label: string; value: string };

const navItems: NavItem[] = [
  { href: "/", label: "Dashboard", value: "dashboard" },
  { href: "/scenario-lab", label: "Scenario Lab", value: "scenario" },
  { href: "/recommendation", label: "Recommendation", value: "recommendation" },
  { href: "/audit", label: "Audit & Replay", value: "audit" },
  { href: "/admin", label: "Admin", value: "admin" }
];

function valueFromPath(pathname: string): string {
  const match = navItems.find((item) => item.href === pathname);
  return match?.value ?? "dashboard";
}

export function Shell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const selectedValue = valueFromPath(pathname);

  return (
    <div className={styles.root}>
      <header className={styles.header}>
        <div className={styles.brand}>
          <Body1 weight="semibold">CCC ASE</Body1>
        </div>
        <TabList selectedValue={selectedValue}>
          {navItems.map((item) => (
            <Tab key={item.value} value={item.value}>
              <Link className={styles.link} href={item.href}>
                {item.label}
              </Link>
            </Tab>
          ))}
        </TabList>
      </header>
      <Divider />
      <main className={styles.main}>{children}</main>
    </div>
  );
}

