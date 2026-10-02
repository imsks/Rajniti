import { render, screen, fireEvent } from "@testing-library/react";
import SaranshSection from "@/components/marketing/SaranshSection";

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
const UTM = (placement: string) =>
  `utm_source=rajniti&utm_medium=referral&utm_campaign=saransh_cross_promo&utm_content=${placement}`;
const BUTTON_URL = `${DEFAULT_URL}?${UTM("home_section")}`;
const TILE_URL = `${DEFAULT_URL}?${UTM("home_section_tile")}`;

async function renderSection() {
  render(<SaranshSection />);
}

describe("SaranshSection", () => {
  beforeEach(() => {
    trackEvent.mockClear();
  });

  it("renders the cross-promo copy and a safe external link to the default URL", async () => {
    await renderSection();

    expect(
      screen.getByRole("heading", { name: /Meet Saransh/i }),
    ).toBeInTheDocument();

    const link = screen.getByRole("link", {
      name: /Read the news on Saransh/i,
    });
    expect(link).toHaveAttribute("href", BUTTON_URL);
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");
  });

  it("renders the sibling lockup with a safe external Saransh tile", async () => {
    await renderSection();

    const tile = screen.getByRole("link", {
      name: /What the news says about them/i,
    });
    expect(tile).toHaveAttribute("href", TILE_URL);
    expect(tile).toHaveAttribute("target", "_blank");
    expect(tile).toHaveAttribute("rel", "noopener noreferrer");

    expect(
      screen.getByText("What your representatives promised"),
    ).toBeInTheDocument();
  });

  it("fires saransh_click with the home_section placement on click", async () => {
    await renderSection();

    fireEvent.click(
      screen.getByRole("link", { name: /Read the news on Saransh/i }),
    );

    expect(trackEvent).toHaveBeenCalledTimes(1);
    expect(trackEvent).toHaveBeenCalledWith("saransh_click", {
      link_url: BUTTON_URL,
      page_location: "home_saransh",
      placement: "home_section",
    });
  });

  it("fires saransh_click with the home_section_tile placement for the tile", async () => {
    await renderSection();

    fireEvent.click(
      screen.getByRole("link", { name: /What the news says about them/i }),
    );

    expect(trackEvent).toHaveBeenCalledWith("saransh_click", {
      link_url: TILE_URL,
      page_location: "home_saransh",
      placement: "home_section_tile",
    });
  });

  it("counts middle-click new-tab opens but ignores right-click", async () => {
    await renderSection();

    const link = screen.getByRole("link", {
      name: /Read the news on Saransh/i,
    });

    auxClick(link, 2);
    expect(trackEvent).not.toHaveBeenCalled();

    auxClick(link, 1);
    expect(trackEvent).toHaveBeenCalledTimes(1);
    expect(trackEvent).toHaveBeenCalledWith("saransh_click", {
      link_url: BUTTON_URL,
      page_location: "home_saransh",
      placement: "home_section",
    });
  });
});
