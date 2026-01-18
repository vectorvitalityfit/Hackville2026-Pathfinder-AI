import { ReactNode } from "react";
import { BottomNavigation } from "./BottomNavigation";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <>
      {/* Global ARIA Live Region - placed at root for all announcements */}
      <div
        id="aria-live-region"
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      />
      
      <div className="flex min-h-screen flex-col">
        <a
          href="#main-content"
          className="skip-link"
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              const main = document.getElementById("main-content");
              main?.focus();
            }
          }}
        >
          Skip to main content
        </a>
        <main
          id="main-content"
          className="flex-1 pb-24"
          tabIndex={-1}
          role="main"
        >
          {children}
        </main>
        <BottomNavigation />
      </div>
    </>
  );
}
