const DEFAULT_URL = "https://saransh-app.vercel.app";

async function loadModule(saranshUrl?: string) {
  jest.resetModules();
  if (saranshUrl) {
    process.env.NEXT_PUBLIC_SARANSH_URL = saranshUrl;
  } else {
    delete process.env.NEXT_PUBLIC_SARANSH_URL;
  }
  return import("@/lib/constants/saransh");
}

describe("buildSaranshUrl", () => {
  const originalUrl = process.env.NEXT_PUBLIC_SARANSH_URL;

  afterEach(() => {
    if (originalUrl === undefined) {
      delete process.env.NEXT_PUBLIC_SARANSH_URL;
    } else {
      process.env.NEXT_PUBLIC_SARANSH_URL = originalUrl;
    }
  });

  it("appends the four campaign parameters with the placement as utm_content", async () => {
    const { buildSaranshUrl } = await loadModule();

    const url = new URL(buildSaranshUrl("home_section"));

    expect(url.origin).toBe(DEFAULT_URL);
    expect(url.searchParams.get("utm_source")).toBe("rajniti");
    expect(url.searchParams.get("utm_medium")).toBe("referral");
    expect(url.searchParams.get("utm_campaign")).toBe("saransh_cross_promo");
    expect(url.searchParams.get("utm_content")).toBe("home_section");
  });

  it("uses a distinct utm_content per placement", async () => {
    const { buildSaranshUrl } = await loadModule();

    const placements = [
      "home_section",
      "home_section_tile",
      "dashboard_banner",
      "navbar",
      "footer",
    ] as const;

    for (const placement of placements) {
      expect(
        new URL(buildSaranshUrl(placement)).searchParams.get("utm_content"),
      ).toBe(placement);
    }
  });

  it("honours the NEXT_PUBLIC_SARANSH_URL override", async () => {
    const { buildSaranshUrl } = await loadModule("https://saransh.example.com");

    expect(buildSaranshUrl("footer")).toBe(
      "https://saransh.example.com?utm_source=rajniti&utm_medium=referral&utm_campaign=saransh_cross_promo&utm_content=footer",
    );
  });

  it("keeps an existing query string on the base URL", async () => {
    const { buildSaranshUrl } = await loadModule(
      "https://saransh.example.com/?ref=x",
    );

    const url = new URL(buildSaranshUrl("navbar"));
    expect(url.searchParams.get("ref")).toBe("x");
    expect(url.searchParams.get("utm_content")).toBe("navbar");
  });

  it("carries no user-identifying parameters", async () => {
    const { buildSaranshUrl } = await loadModule();

    const params = [
      ...new URL(buildSaranshUrl("home_section")).searchParams.keys(),
    ];

    expect(params).toEqual([
      "utm_source",
      "utm_medium",
      "utm_campaign",
      "utm_content",
    ]);
  });
});
