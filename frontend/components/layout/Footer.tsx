"use client";

import React from "react";
import Text from "@/components/ui/Text";
import Link from "@/components/ui/Link";
import { useAnalytics } from "@/hooks/useAnalytics";
import { useSaranshLink } from "@/hooks/useSaranshLink";
import { SARANSH_URL } from "@/lib/constants/saransh";

export default function Footer() {
  const { trackEvent } = useAnalytics();
  const saranshLink = useSaranshLink();
  // Footer Saransh link fires both `nav_click` and `saransh_click` by design.
  const saranshFooterLink = saranshLink("footer", "footer");
  return (
    <footer className="bg-[#0F1F3D] dark:bg-gray-950 text-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col items-center text-center gap-6">
          {/* Logo + tagline */}
          <div className="flex flex-col gap-2">
            <span className="font-serif text-2xl font-semibold">
              Raj<span className="text-orange-500">niti</span>
            </span>
            <Text variant="small" className="text-gray-400">
              Open source · Built for India · Community driven
            </Text>
            <p className="text-gray-500 text-sm mt-1">Built with ❤️ in 🇮🇳</p>
          </div>

          {/* Links */}
          <nav
            className="flex flex-wrap justify-center gap-4 pt-2 border-t border-white/10 w-full max-w-lg"
            aria-label="Footer links"
          >
            <Link
              href="/politicians"
              onClick={() =>
                trackEvent("nav_click", {
                  link_text: "Politicians",
                  link_url: "/politicians",
                  nav_section: "footer",
                })
              }
              className="text-gray-400 hover:text-white transition-colors text-sm"
            >
              Politicians
            </Link>
            <Link
              href="/dashboard"
              onClick={() =>
                trackEvent("nav_click", {
                  link_text: "Dashboard",
                  link_url: "/dashboard",
                  nav_section: "footer",
                })
              }
              className="text-gray-400 hover:text-white transition-colors text-sm"
            >
              Dashboard
            </Link>
            <Link
              href="https://github.com/imsks/rajniti"
              external
              onClick={() =>
                trackEvent("nav_click", {
                  link_text: "GitHub",
                  link_url: "https://github.com/imsks/rajniti",
                  nav_section: "footer",
                })
              }
              className="text-gray-400 hover:text-white transition-colors text-sm"
            >
              GitHub
            </Link>
            <Link
              href="/#about"
              onClick={() =>
                trackEvent("nav_click", {
                  link_text: "About",
                  link_url: "/#about",
                  nav_section: "footer",
                })
              }
              className="text-gray-400 hover:text-white transition-colors text-sm"
            >
              About
            </Link>
            <Link
              external
              href={saranshFooterLink.href}
              onClick={() => {
                trackEvent("nav_click", {
                  link_text: "Saransh",
                  link_url: SARANSH_URL,
                  nav_section: "footer",
                });
                saranshFooterLink.onClick();
              }}
              onAuxClick={(event: React.MouseEvent) => {
                if (event.button !== 1) return;
                trackEvent("nav_click", {
                  link_text: "Saransh",
                  link_url: SARANSH_URL,
                  nav_section: "footer",
                });
                saranshFooterLink.onAuxClick(event);
              }}
              className="text-gray-400 hover:text-white transition-colors text-sm"
            >
              Saransh
            </Link>
            <Link
              href="/contributors"
              onClick={() =>
                trackEvent("nav_click", {
                  link_text: "Contributors",
                  link_url: "/contributors",
                  nav_section: "footer",
                })
              }
              className="text-gray-400 hover:text-white transition-colors text-sm"
            >
              Contributors
            </Link>
          </nav>
        </div>
      </div>
    </footer>
  );
}
