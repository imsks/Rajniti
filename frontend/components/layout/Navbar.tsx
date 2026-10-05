"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";
import { Menu, X } from "lucide-react";
import NextImage from "next/image";
import UserButton from "@/components/auth/UserButton";
import Text from "@/components/ui/Text";
import Link from "@/components/ui/Link";
import ThemeToggle from "@/components/ui/ThemeToggle";
import { useAnalytics } from "@/hooks/useAnalytics";
import { buildSaranshUrl, SARANSH_URL } from "@/lib/constants/saransh";

interface NavbarProps {
  /** @deprecated Use sticky only; nav links are identical on every page. */
  variant?: "default" | "dashboard";
  sticky?: boolean;
}

/** Public links always visible in the navbar. App links live in the profile menu. */
const NAV_LINKS: ReadonlyArray<{
  label: string;
  href: string;
  external?: boolean;
}> = [
  { label: "About", href: "/#about" },
  { label: "Contribute", href: "/#contribute" },
  {
    label: "Saransh",
    href: SARANSH_URL,
    external: true,
  },
  {
    label: "Found a Bug?",
    href: "https://github.com/imsks/rajniti/issues/new",
    external: true,
  },
];

export default function Navbar({ sticky = false }: NavbarProps) {
  const stickyClasses = sticky ? "sticky top-0" : "";
  const { trackEvent } = useAnalytics();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const menuPanelRef = useRef<HTMLDivElement>(null);
  const menuId = useId();

  const trackNav = (
    text: string,
    url: string,
    section: "navbar" | "navbar_mobile" = "navbar",
  ) =>
    trackEvent("nav_click", {
      link_text: text,
      link_url: url,
      nav_section: section,
    });

  const closeMenu = useCallback((returnFocus = false) => {
    setIsMenuOpen(false);
    if (returnFocus) menuButtonRef.current?.focus();
  }, []);

  const toggleMenu = () => {
    const nextOpen = !isMenuOpen;
    setIsMenuOpen(nextOpen);
    trackEvent("mobile_menu_toggle", { action: nextOpen ? "open" : "close" });
  };

  useEffect(() => {
    if (!isMenuOpen) return;

    const isInsideMenu = (target: EventTarget | null) =>
      target instanceof Node &&
      (menuPanelRef.current?.contains(target) ||
        menuButtonRef.current?.contains(target));

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") closeMenu(true);
    };
    const onOutside = (event: Event) => {
      if (!isInsideMenu(event.target)) closeMenu();
    };

    document.addEventListener("keydown", onKeyDown);
    document.addEventListener("pointerdown", onOutside);
    document.addEventListener("focusin", onOutside);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("pointerdown", onOutside);
      document.removeEventListener("focusin", onOutside);
    };
  }, [isMenuOpen, closeMenu]);

  /** Fires the placement-specific events a link needs, on top of nav_click. */
  const trackLinkExtras = (
    label: string,
    section: "navbar" | "navbar_mobile",
  ) => {
    if (label === "Found a Bug?") {
      trackEvent("contribute_click", {
        contribute_type: "bug",
        page_location: section,
      });
    }
    if (label === "Saransh" && section === "navbar_mobile") {
      trackEvent("saransh_click", {
        link_url: buildSaranshUrl("navbar_mobile"),
        page_location: "navbar_mobile",
        placement: "navbar_mobile",
      });
    }
  };

  return (
    <header
      className={`relative z-50 border-b border-orange-200 dark:border-gray-700 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm ${stickyClasses}`}
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link
            href="/"
            onClick={() => trackNav("Logo", "/")}
            className="flex items-center gap-2 no-underline"
          >
            <div className="w-7 h-7">
              <NextImage
                src="/logo/voting-box.svg"
                alt="Rajniti Logo"
                width={28}
                height={28}
                className="dark:filter-[invert(1)_brightness(2)]"
              />
            </div>
            <Text
              variant="h3"
              className="text-[#0F1F3D] dark:text-white font-bold tracking-tight font-poppins mt-2"
            >
              Raj
              <span>
                <span className="text-orange-600">niti</span>
              </span>
            </Text>
          </Link>

          <div className="flex items-center gap-4">
            <nav className="hidden md:flex gap-6 items-center">
              {NAV_LINKS.map(({ label, href, external }) => {
                const isSaransh = href === SARANSH_URL;
                // Saransh links carry UTM attribution and also fire
                // `saransh_click` alongside the usual `nav_click`.
                const linkHref = isSaransh ? saranshNavLink.href : href;

                return (
                <Link
                  key={label}
                  href={linkHref}
                  variant="nav"
                  {...(external ? { external: true, target: "_blank" } : {})}
                  {...(isSaransh
                    ? {
                        onAuxClick: (event: React.MouseEvent) => {
                          saranshNavLink.onAuxClick(event);
                          if (event.button === 1) trackNav(label, href);
                        },
                      }
                    : {})}
                  onClick={() => {
                    trackNav(label, href);
                    trackLinkExtras(label, "navbar");
                  }}
                >
                  {label}
                </Link>
                );
              })}
            </nav>

            <ThemeToggle />
            <UserButton />

            <button
              ref={menuButtonRef}
              type="button"
              onClick={toggleMenu}
              aria-label={isMenuOpen ? "Close menu" : "Open menu"}
              aria-expanded={isMenuOpen}
              aria-controls={menuId}
              className="md:hidden flex h-11 w-11 items-center justify-center rounded-md text-gray-600 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
            >
              {isMenuOpen ? (
                <X className="h-6 w-6" aria-hidden="true" />
              ) : (
                <Menu className="h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      {isMenuOpen && (
        <div
          ref={menuPanelRef}
          id={menuId}
          className="md:hidden border-t border-orange-200 dark:border-gray-700 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm"
        >
          <nav
            aria-label="Mobile"
            className="mx-auto flex max-w-7xl flex-col px-4 py-2 sm:px-6"
          >
            {NAV_LINKS.map(({ label, href, external }) => {
              const url =
                label === "Saransh" ? buildSaranshUrl("navbar_mobile") : href;
              return (
                <Link
                  key={label}
                  href={url}
                  variant="nav"
                  {...(external ? { external: true, target: "_blank" } : {})}
                  className="flex min-h-[44px] items-center"
                  onClick={() => {
                    trackNav(label, url, "navbar_mobile");
                    trackLinkExtras(label, "navbar_mobile");
                    closeMenu();
                  }}
                >
                  {label}
                </Link>
              );
            })}
          </nav>
        </div>
      )}
    </header>
  );
}
