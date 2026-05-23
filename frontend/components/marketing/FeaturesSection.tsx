"use client";

import Text from "@/components/ui/Text";
import Image from "next/image";
import { motion } from "framer-motion";

export default function FeaturesSection() {
  return (
    <section id="about" className="py-20 bg-white dark:bg-gray-900">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <div className="flex items-center justify-center gap-3 text-md font-semibold text-orange-600 mb-4 uppercase tracking-wider">
            <div className="w-8 h-0.5 border-t-2  border-orange-600"></div>
            What You&apos;ll Find
          </div>
          <h2 className="text-xl md:text-4xl lg:text-5xl font-serif font-bold text-[#0F1F3D] dark:text-white mb-6">
            Transparency for Every{" "}
            <span className="text-orange-600 italic">Citizen</span>
          </h2>
          <Text
            variant="body"
            className="text-gray-600 dark:text-gray-400 max-w-3xl mx-auto"
          >
            We&apos;re building the most transparent and comprehensive
            database of Indian elected representatives.
          </Text>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5, delay: 0.1 }}
            whileHover={{ y: -8, transition: { duration: 0.2 } }}
            className="rounded-2xl p-8 border border-black/10 dark:border-gray-700"
          >
            <div className="text-4xl mb-4">
              <Image
                src="/logo/parliament.png"
                alt="Parliament Logo"
                width={40}
                height={40}
                className="h-10 w-10"
              />
            </div>
            <Text
              variant="h4"
              weight="bold"
              className="text-[#0F1F3D] dark:text-white mb-3"
            >
              Members of Parliament
            </Text>
            <Text variant="body" color="muted">
              Browse all winning Lok Sabha MPs — their party, constituency,
              state, and election history.
            </Text>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5, delay: 0.2 }}
            whileHover={{ y: -8, transition: { duration: 0.2 } }}
            className=" rounded-2xl p-8 border border-black/10 dark:border-gray-700"
          >
            <div className="text-4xl mb-4">
              <Image
                src="/logo/Assembly.png"
                alt="State Assembly Logo"
                width={40}
                height={40}
                className="h-10 w-10"
              />
            </div>
            <Text
              variant="h4"
              weight="bold"
              className="text-[#0F1F3D] dark:text-white mb-3"
            >
              State Assembly MLAs
            </Text>
            <Text variant="body" color="muted">
              Explore elected MLAs from state assemblies across India with
              detailed political backgrounds.
            </Text>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5, delay: 0.3 }}
            whileHover={{ y: -8, transition: { duration: 0.2 } }}
            className=" rounded-2xl p-8 border border-black/10 dark:border-gray-700"
          >
            <div className="text-4xl mb-4">
              <Image
                src="/logo/Profile.png"
                alt="Rich Profile Logo"
                width={36}
                height={36}
                className="h-9 w-9"
              />
            </div>
            <Text
              variant="h4"
              weight="bold"
              className="text-[#0F1F3D] dark:text-white mb-3 "
            >
              Rich Profiles
            </Text>
            <Text variant="body" color="muted">
              Education, family, criminal records, social media, and more —
              enriched with community contributions.
            </Text>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
