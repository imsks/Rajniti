import dynamic from "next/dynamic"
import { Navbar, Footer } from "@/components/layout"
import { HeroSection } from "@/components/marketing"
import ScrollReset from "@/components/marketing/ScrollReset"

// Below-fold sections: code-split to reduce initial JS bundle (~150 KiB savings)
const FeaturesSection = dynamic(
  () => import("@/components/marketing/FeaturesSection"),
  { ssr: true }
)
const PreambleSection = dynamic(
  () => import("@/components/PreambleSection"),
  { ssr: true }
)
const ContributeSection = dynamic(
  () => import("@/components/marketing/ContributeSection"),
  { ssr: true }
)
const ContributorsSection = dynamic(
  () => import("@/components/marketing/ContributorsSection"),
  { ssr: true }
)

export default function Home() {
  return (
    <div className="min-h-screen overflow-x-hidden bg-linear-to-b from-orange-50 via-white to-green-50 dark:from-[#070b16] dark:via-[#0b1324] dark:to-[#101a32]">
      <ScrollReset />
      <Navbar />
      <HeroSection />
      <FeaturesSection />
      <PreambleSection />
      <ContributeSection />
      <ContributorsSection />
      <Footer />
    </div>
  );
}
