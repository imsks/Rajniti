"use client";

import { signIn } from "next-auth/react";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

function TestSignInContent() {
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (process.env.NEXT_PUBLIC_ENABLE_TEST_AUTH !== "true") {
      setError("Test auth is disabled");
      return;
    }

    const userId = searchParams.get("userId");
    const onboardingCompleted =
      searchParams.get("onboardingCompleted") ?? "false";
    const callbackUrl = searchParams.get("callbackUrl") ?? "/dashboard";

    if (!userId) {
      setError("Missing userId");
      return;
    }

    void signIn("test-credentials", {
      userId,
      onboardingCompleted,
      callbackUrl,
      redirect: true,
    }).catch((signInError) => {
      setError(
        signInError instanceof Error ? signInError.message : "Sign-in failed",
      );
    });
  }, [searchParams]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-gray-600">Signing in for tests…</p>
    </div>
  );
}

export default function TestSignInPage() {
  if (process.env.NEXT_PUBLIC_ENABLE_TEST_AUTH !== "true") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Not available</p>
      </div>
    );
  }

  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <p className="text-gray-600">Loading…</p>
        </div>
      }
    >
      <TestSignInContent />
    </Suspense>
  );
}
