import type { Metadata } from "next";
import { Lora, Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import AuthProvider from "@/components/auth/AuthProvider";
import GoogleAnalytics from "@/components/analytics/GoogleAnalytics";
import AnalyticsPageViewTracker from "@/components/analytics/AnalyticsPageViewTracker";
import ThemeProvider from "@/components/providers/ThemeProvider";
import MotionProvider from "@/components/providers/MotionProvider";
import JsonLd from "@/components/seo/JsonLd";
import { buildWebSiteJsonLd } from "@/lib/seo/json-ld";
import {
    buildDefaultOg,
    buildDefaultTwitter,
    defaultDescription,
    getSiteUrl,
    SITE_NAME,
} from "@/lib/seo/site";

const lora = Lora({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
  variable: "--font-serif",
  display: "swap",
});

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
    metadataBase: new URL(getSiteUrl()),
    title: {
        default: `${SITE_NAME} — Indian MPs & MLAs`,
        template: `%s | ${SITE_NAME}`,
    },
    description: defaultDescription,
    applicationName: SITE_NAME,
    authors: [{ name: "Rajniti contributors", url: "https://github.com/imsks/rajniti" }],
    creator: "Rajniti",
    publisher: "Rajniti",
    formatDetection: {
        email: false,
        address: false,
        telephone: false,
    },
    openGraph: {
        ...buildDefaultOg(),
        title: `${SITE_NAME} — Know Your Elected Representatives`,
        description: defaultDescription,
    },
    twitter: buildDefaultTwitter(),
    robots: {
        index: true,
        follow: true,
        googleBot: {
            index: true,
            follow: true,
        },
    },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${lora.variable} ${jakarta.variable}`} suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var theme = localStorage.getItem('theme');
                  if (theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
                    document.documentElement.classList.add('dark');
                  }
                } catch(e) {}
              })();
            `,
          }}
        />
      </head>
      <body className="antialiased">
        <JsonLd data={buildWebSiteJsonLd()} />
        <GoogleAnalytics />
        <AnalyticsPageViewTracker />
        <AuthProvider>
          <ThemeProvider>
            <MotionProvider>
              {children}
            </MotionProvider>
          </ThemeProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
