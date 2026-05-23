"use client";

import { Suspense, useCallback, useMemo, useState } from "react";
import { useSession } from "next-auth/react";
import OnboardingGate from "@/components/auth/OnboardingGate";
import { motion, AnimatePresence } from "framer-motion";
import PoliticalInclinationStep from "@/components/onboarding/PoliticalInclinationStep";
import UsernameStep from "@/components/onboarding/UsernameStep";
import UserDetailsStep from "@/components/onboarding/UserDetailsStep";
import PreferencesStep from "@/components/onboarding/PreferencesStep";
import { userService } from "@/lib/api/user";
import { useAnalytics } from "@/hooks/useAnalytics";
import { ROUTES } from "@/lib/routes";

const COPY = {
  signInRequired: "Please sign in to complete onboarding",
  onboardingFailed: "Failed to complete onboarding. Please try again.",
  stepProgress: (current: number, total: number) =>
    `Step ${current} of ${total}`,
  completeCta: "Complete Onboarding 🚀",
  saving: "Saving...",
  continue: "Continue",
  back: "Back",
} as const;

interface OnboardingData {
  political_ideology: string;
  phone: string;
  state: string;
  city: string;
  age_group: string;
  preferred_parties: string[];
  topics_of_interest: string[];
  username: string;
}

const INITIAL_DATA: OnboardingData = {
  political_ideology: "",
  phone: "",
  state: "",
  city: "",
  age_group: "",
  preferred_parties: [],
  topics_of_interest: [],
  username: "",
};

const STEP_LABELS = [
  "Political Inclination",
  "Basic Details",
  "Preferences",
  "Username",
] as const;

const STEP_COUNT = STEP_LABELS.length;

const stepMotionProps = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
  transition: { duration: 0.3 },
} as const;

function LoadingFallback() {
  return (
    <div className="min-h-screen bg-linear-to-b from-orange-50 via-white to-green-50 flex items-center justify-center">
      <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-orange-500 border-t-transparent" />
    </div>
  );
}

/**
 * useAnalytics → useSearchParams() requires a Suspense ancestor during static
 * generation (Next.js CSR bailout). The shell provides the boundary.
 */
export default function OnboardingPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <OnboardingGate
        redirectIfIncomplete={false}
        redirectIfComplete
        blockUntilReady={false}
        fallback={<LoadingFallback />}
      >
        <OnboardingContent />
      </OnboardingGate>
    </Suspense>
  );
}

function OnboardingContent() {
  const { data: session, status, update } = useSession();
  const { trackEvent } = useAnalytics();

  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [usernameValid, setUsernameValid] = useState(false);
  const [formData, setFormData] = useState<OnboardingData>(INITIAL_DATA);

  const sessionReady = status !== "loading";
  const userId = session?.user?.id;

  const updateField = useCallback(
    (field: keyof OnboardingData, value: string | string[]) => {
      setFormData((prev) => ({ ...prev, [field]: value }));
    },
    [],
  );

  const canProceed = useMemo(() => {
    switch (step) {
      case 1:
        return formData.political_ideology !== "";
      case 2:
        return formData.state !== "" && formData.age_group !== "";
      case 3:
        return true;
      case 4:
        return formData.username !== "" && usernameValid;
      default:
        return false;
    }
  }, [step, formData, usernameValid]);

  const completeSessionAndRedirect = useCallback(async () => {
    await update({ onboardingCompleted: true });
    window.location.href = ROUTES.dashboard;
  }, [update]);

  const handleSubmit = useCallback(async () => {
    if (!userId) {
      alert(COPY.signInRequired);
      return;
    }

    setSubmitting(true);
    try {
      await userService.updateUser(userId, {
        political_ideology: formData.political_ideology,
        username: formData.username,
        phone: formData.phone,
        state: formData.state,
        city: formData.city,
        age_group: formData.age_group,
        preferred_parties: formData.preferred_parties.join(", "),
        topics_of_interest: formData.topics_of_interest.join(", "),
        onboarding_completed: true,
      });

      trackEvent("onboarding_complete", {
        political_ideology: formData.political_ideology,
      });

      await completeSessionAndRedirect();
    } catch (error) {
      console.error("Onboarding failed:", error);
      alert(error instanceof Error ? error.message : COPY.onboardingFailed);
    } finally {
      setSubmitting(false);
    }
  }, [userId, formData, trackEvent, completeSessionAndRedirect]);

  const handleNext = useCallback(() => {
    trackEvent("onboarding_step_complete", {
      step,
      step_name: STEP_LABELS[step - 1],
    });
    setStep((s) => s + 1);
  }, [step, trackEvent]);

  if (!sessionReady) {
    return <LoadingFallback />;
  }

  return (
    <div className="min-h-screen bg-linear-to-b from-orange-50 via-white to-green-50 py-12 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-2xl mx-auto"
      >
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mb-8"
        >
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">
              {COPY.stepProgress(step, STEP_COUNT)}
            </span>
            <span className="text-sm text-gray-500">
              {STEP_LABELS[step - 1]}
            </span>
          </div>

          <div className="flex gap-1.5 mb-2">
            {STEP_LABELS.map((_, i) => (
              <div
                key={i}
                className={`h-2 flex-1 rounded-full transition-all duration-500 ${
                  i < step
                    ? "bg-gradient-to-r from-orange-500 to-green-500"
                    : "bg-gray-200"
                }`}
              />
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bg-white rounded-2xl shadow-xl p-8 border border-orange-100"
        >
          <AnimatePresence mode="wait">
            {step === 1 && (
              <motion.div key="step1" {...stepMotionProps}>
                <PoliticalInclinationStep
                  value={formData.political_ideology}
                  onChange={(val) => updateField("political_ideology", val)}
                />
              </motion.div>
            )}

            {step === 2 && (
              <motion.div key="step2" {...stepMotionProps}>
                <UserDetailsStep
                  formData={{
                    phone: formData.phone,
                    state: formData.state,
                    city: formData.city,
                    age_group: formData.age_group,
                  }}
                  onChange={(field, value) =>
                    updateField(field as keyof OnboardingData, value)
                  }
                />
              </motion.div>
            )}

            {step === 3 && (
              <motion.div key="step3" {...stepMotionProps}>
                <PreferencesStep
                  formData={{
                    preferred_parties: formData.preferred_parties,
                    topics_of_interest: formData.topics_of_interest,
                  }}
                  onChange={(field, values) =>
                    updateField(field as keyof OnboardingData, values)
                  }
                />
              </motion.div>
            )}

            {step === 4 && (
              <motion.div key="step4" {...stepMotionProps}>
                <UsernameStep
                  value={formData.username}
                  onChange={(val) => updateField("username", val)}
                  onValidation={setUsernameValid}
                />
              </motion.div>
            )}
          </AnimatePresence>

          <div className="flex gap-4 mt-8">
            {step > 1 && (
              <motion.button
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setStep((s) => s - 1)}
                disabled={submitting}
                className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50 transition-all disabled:opacity-50"
              >
                {COPY.back}
              </motion.button>
            )}

            {step < STEP_COUNT ? (
              <motion.button
                whileHover={{ scale: canProceed ? 1.02 : 1 }}
                whileTap={{ scale: canProceed ? 0.98 : 1 }}
                onClick={handleNext}
                disabled={!canProceed || submitting}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg text-white font-semibold hover:from-orange-600 hover:to-orange-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {COPY.continue}
              </motion.button>
            ) : (
              <motion.button
                whileHover={{ scale: !submitting ? 1.02 : 1 }}
                whileTap={{ scale: !submitting ? 0.98 : 1 }}
                onClick={handleSubmit}
                disabled={submitting || !canProceed}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 rounded-lg text-white font-semibold hover:from-green-600 hover:to-green-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? COPY.saving : COPY.completeCta}
              </motion.button>
            )}
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
