import "./styles.css";
import type { ReactNode } from "react";

export const metadata = { title: "Agentic QA OS", description: "Evidence-aware autonomous quality engineering" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
