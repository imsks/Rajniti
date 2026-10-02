import { render, screen, fireEvent } from "@testing-library/react";
import SaranshBanner from "@/components/marketing/SaranshBanner";

const trackEvent = jest.fn();

/** jsdom/RTL has no `fireEvent.auxClick`, so dispatch the native event. */
const auxClick = (element: Element, button: number) =>
  fireEvent(
    element,
    new MouseEvent("auxclick", { bubbles: true, cancelable: true, button }),
  );

jest.mock("@/hooks/useAnalytics", () => ({
  useAnalytics: () => ({ trackEvent }),
}));

const DEFAULT_URL = "https://saransh-app.vercel.app";
const BANNER_URL = `${DEFAULT_URL}?utm_source=rajniti&utm_medium=referral&utm_campaign=saransh_cross_promo&utm_content=dashboard_banner`;

async function renderBanner(props = {}) {
  render(<SaranshBanner {...props} />);
}

describe("SaranshBanner", () => {
  beforeEach(() => {
    trackEvent.mockClear();
  });

  it("renders a safe external link to Saransh", async () => {
    await renderBanner();

    const link = screen.getByRole("link", { name: /Meet Saransh/i });
    expect(link).toHaveAttribute("href", BANNER_URL);
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");
  });

  it("fires saransh_click with the dashboard page location by default", async () => {
    await renderBanner();

    fireEvent.click(screen.getByRole("link", { name: /Meet Saransh/i }));

    expect(trackEvent).toHaveBeenCalledTimes(1);
    expect(trackEvent).toHaveBeenCalledWith("saransh_click", {
      link_url: BANNER_URL,
      page_location: "dashboard_saransh",
      placement: "dashboard_banner",
    });
  });

  it("allows overriding the analytics page location", async () => {
    await renderBanner({ pageLocation: "profile_saransh" });

    fireEvent.click(screen.getByRole("link", { name: /Meet Saransh/i }));

    expect(trackEvent).toHaveBeenCalledWith("saransh_click", {
      link_url: BANNER_URL,
      page_location: "profile_saransh",
      placement: "dashboard_banner",
    });
  });

  it("counts middle-click new-tab opens", async () => {
    await renderBanner();

    auxClick(screen.getByRole("link", { name: /Meet Saransh/i }), 1);

    expect(trackEvent).toHaveBeenCalledTimes(1);
    expect(trackEvent).toHaveBeenCalledWith("saransh_click", {
      link_url: BANNER_URL,
      page_location: "dashboard_saransh",
      placement: "dashboard_banner",
    });
  });
});
