import "@/app/globals.css";

import type { Metadata } from "next";
import { ReactNode } from "react";

import { AppProviders } from "@/app/providers";
import { Shell } from "@/components/Shell/Shell";

export const metadata: Metadata = {
  title: "CCC ASE",
  description: "Autonomous Strategy Engine PoC UI"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppProviders>
          <Shell>{children}</Shell>
        </AppProviders>
      </body>
    </html>
  );
}

