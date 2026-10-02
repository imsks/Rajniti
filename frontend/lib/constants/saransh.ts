/** Saransh frontend URL — env-driven so the destination can change without a code change. */
export const SARANSH_URL =
  process.env.NEXT_PUBLIC_SARANSH_URL || "https://saransh-app.vercel.app";
