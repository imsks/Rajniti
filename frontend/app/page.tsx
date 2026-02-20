import PreambleSection from "@/components/PreambleSection";
import { Navbar, Footer } from "@/components/layout";
import Text from "@/components/ui/Text";
import Link from "@/components/ui/Link";
import Button from "@/components/ui/Button";
import { Database, Zap, Github } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50">
      <Navbar variant="default" />

      {/* Hero Section */}
      <section className="py-20 sm:py-32 relative z-[2]">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="mb-8 flex justify-center">
              <div className="rounded-full bg-gradient-to-r from-orange-500 via-white to-green-500 p-1">
                <div className="rounded-full bg-white px-6 py-2">
                  <span className="text-sm font-semibold text-gray-700">
                    Built for 🇮🇳 Democracy
                  </span>
                </div>
              </div>
            </div>

            <Text variant="h1" className="text-gray-900 mb-6">
              Empowering Democracy Through{" "}
              <span className="block bg-gradient-to-r from-orange-600 via-orange-500 to-green-600 bg-clip-text text-transparent">
                Open Election Data
              </span>
            </Text>

            <Text
              variant="body"
              className="mx-auto max-w-2xl text-gray-600 mb-10"
            >
              Rajniti is a clean, lightweight REST API providing comprehensive
              Indian Election Commission data. Access 50,000+ records across Lok
              Sabha and Assembly elections - free and open source.
            </Text>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button
                href="/dashboard"
                size="lg"
                rightIcon={
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                }
              >
                View Dashboard
              </Button>

              <Button
                href="https://github.com/imsks/rajniti"
                external
                variant="secondary"
                size="lg"
                leftIcon={
                  <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      fillRule="evenodd"
                      d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                      clipRule="evenodd"
                    />
                  </svg>
                }
              >
                View on GitHub
              </Button>
            </div>
          </div>
        </div>

        {/* Decorative Elements */}
        <div className="absolute top-0 left-0 w-72 h-72 bg-orange-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse z-[1] pointer-events-none"></div>
        <div className="absolute bottom-0 right-0 w-72 h-72 bg-green-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse delay-1000 z-[1] pointer-events-none"></div>
      </section>

      {/* Why We're Building Section */}
      <section id="about" className="py-28 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-start">
            <div>
              <Text
                variant="small"
                className="tracking-widest text-gray-500 mb-4"
              >
                WHY RAJNITI
              </Text>

              <Text
                variant="h2"
                className="mb-6 leading-tight
          bg-gradient-to-r from-orange-600 via-gray-500 to-green-500
          bg-clip-text text-transparent"
              >
                Democracy needs data.
               <br />
                We make it accessible.
              </Text>

              <Text
                variant="body"
                className="text-gray-600 leading-relaxed max-w-xl text-lg"
              >
                Rajniti exists to remove barriers between citizens and election
                data. No gatekeeping. No friction. Just structured, usable
                public information for builders, researchers, and voters.
              </Text>
            </div>

            <div className="relative pl-10">
              <div className="absolute left-4 top-2 bottom-2 w-px bg-gray-200" />

              <div className="space-y-12">
                <div className="relative flex gap-6">
                  <div className="absolute -left-10 bg-white p-2">
                    <Database className="w-6 h-6 text-gray-900" />
                  </div>
                  <div>
                    <Text variant="h4" weight="bold" className="mb-1">
                      Structured election datasets
                    </Text>
                    <Text variant="body" color="muted">
                      50,000+ records across national and state elections —
                      candidates, constituencies, parties, results.
                    </Text>
                  </div>
                </div>

                <div className="relative flex gap-6">
                  <div className="absolute -left-10 bg-white p-2">
                    <Zap className="w-6 h-6 text-gray-900" />
                  </div>
                  <div>
                    <Text variant="h4" weight="bold" className="mb-1">
                      Direct developer access
                    </Text>
                    <Text variant="body" color="muted">
                      Clean REST architecture. Minimal setup. Query data
                      instantly. Build tools, dashboards, and research
                      pipelines.
                    </Text>
                  </div>
                </div>

                <div className="relative flex gap-6">
                  <div className="absolute -left-10 bg-white p-2">
                    <Github className="w-6 h-6 text-gray-900" />
                  </div>
                  <div>
                    <Text variant="h4" weight="bold" className="mb-1">
                      Public infrastructure mindset
                    </Text>
                    <Text variant="body" color="muted">
                      Fully open source. Community maintained. Built for
                      long-term civic value, not short-term growth metrics.
                    </Text>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* We The People of India - Preamble Section */}
      <PreambleSection />

      {/* Contribute Section */}
      <section
        id="contribute"
        className="py-20 bg-gradient-to-r from-orange-600 to-orange-500 text-white"
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <Text variant="h2" className="text-white mb-4">
              Join Our Community
            </Text>
            <Text variant="body" className="text-orange-100 max-w-3xl mx-auto">
              Rajniti is built by contributors who believe in accessible
              democracy. Whether you&apos;re a developer, researcher, or
              democracy enthusiast - there&apos;s a place for you!
            </Text>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <div className="text-3xl mb-3">💻</div>
              <Text variant="h4" weight="bold" className="text-white mb-2">
                Contribute Code
              </Text>
              <Text variant="body" className="text-orange-100 mb-4">
                Help improve the API, add features, fix bugs, or enhance our
                data scraping capabilities.
              </Text>
              <Link
                href="https://github.com/imsks/rajniti/issues"
                external
                className="inline-flex items-center gap-2 text-white font-semibold hover:underline"
              >
                View Open Issues
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </Link>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <div className="text-3xl mb-3">📚</div>
              <Text variant="h4" weight="bold" className="text-white mb-2">
                Improve Documentation
              </Text>
              <Text variant="body" className="text-orange-100 mb-4">
                Help make Rajniti more accessible by improving guides, adding
                examples, or translating docs.
              </Text>
              <Link
                href="https://github.com/imsks/rajniti/blob/main/readme.md"
                external
                className="inline-flex items-center gap-2 text-white font-semibold hover:underline"
              >
                Read the Docs
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </Link>
            </div>
          </div>

          <div className="text-center mt-12">
            <Button
              href="https://github.com/imsks/rajniti/fork"
              external
              className="bg-white text-orange-600 hover:bg-gray-50 border-none shadow-lg hover:shadow-xl hover:scale-105"
              size="lg"
              rightIcon={
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    fillRule="evenodd"
                    d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                    clipRule="evenodd"
                  />
                </svg>
              }
            >
              Fork on GitHub
            </Button>
          </div>
        </div>
      </section>

      {/* API Section - Now Live */}
      <section id="api" className="py-20 bg-gray-50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 rounded-full bg-green-100 px-4 py-2 mb-6">
              <svg
                className="w-5 h-5 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <Text
                variant="small"
                weight="semibold"
                className="text-green-800"
              >
                Now Live
              </Text>
            </div>
            <Text variant="h2" className="text-gray-900 mb-4">
              Interactive Dashboard
            </Text>
            <Text variant="body" className="text-gray-600 max-w-3xl mx-auto">
              Explore our new interactive dashboard to visualize election data,
              search candidates, view party information, and more!
            </Text>
          </div>

          <div className="max-w-3xl mx-auto bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center">
                  <span className="text-orange-600 font-bold">1</span>
                </div>
                <div>
                  <Text
                    variant="h4"
                    weight="semibold"
                    className="text-gray-900 mb-1"
                  >
                    Interactive Dashboard
                  </Text>
                  <Text variant="small" className="text-gray-600">
                    Search candidates, explore elections, view party statistics
                    all in one beautiful interface.
                  </Text>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center">
                  <span className="text-orange-600 font-bold">2</span>
                </div>
                <div>
                  <Text
                    variant="h4"
                    weight="semibold"
                    className="text-gray-900 mb-1"
                  >
                    RESTful API Endpoints
                  </Text>
                  <Text variant="small" className="text-gray-600">
                    Clean, intuitive endpoints for elections, candidates,
                    parties, and constituencies - ready to use.
                  </Text>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center">
                  <span className="text-orange-600 font-bold">3</span>
                </div>
                <div>
                  <Text
                    variant="h4"
                    weight="semibold"
                    className="text-gray-900 mb-1"
                  >
                    Real-time Data Access
                  </Text>
                  <Text variant="small" className="text-gray-600">
                    Access up-to-date election results and candidate information
                    powered by our FastAPI backend.
                  </Text>
                </div>
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-gray-200">
              <Button
                href="/dashboard"
                fullWidth
                rightIcon={
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 7l5 5m0 0l-5 5m5-5H6"
                    />
                  </svg>
                }
              >
                Explore Dashboard
              </Button>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
