import { render, screen, fireEvent } from "@testing-library/react";
import FeaturesSection from "@/components/marketing/FeaturesSection";

const trackEvent = jest.fn();

jest.mock("@/hooks/useAnalytics", () => ({
  useAnalytics: () => ({ trackEvent }),
}));

describe("FeaturesSection", () => {
  beforeEach(() => {
    trackEvent.mockClear();
  });

  it("fires cta_click for the Explore Politicians link", () => {
    render(<FeaturesSection />);

    const link = screen.getByRole("link", { name: /Explore Politicians/i });
    expect(link).toHaveAttribute("href", "/politicians");

    fireEvent.click(link);

    expect(trackEvent).toHaveBeenCalledTimes(1);
    expect(trackEvent).toHaveBeenCalledWith("cta_click", {
      cta_name: "explore_politicians",
      cta_url: "/politicians",
      page_location: "home_features",
    });
  });
});
