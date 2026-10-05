import { render, screen, fireEvent } from "@testing-library/react";
import Footer from "@/components/layout/Footer";

const trackEvent = jest.fn();

jest.mock("@/hooks/useAnalytics", () => ({
  useAnalytics: () => ({ trackEvent }),
}));

const SARANSH_URL = "https://saransh-app.vercel.app";
const SARANSH_FOOTER_URL = `${SARANSH_URL}?utm_source=rajniti&utm_medium=referral&utm_campaign=saransh_cross_promo&utm_content=footer`;

describe("Footer Saransh link", () => {
  beforeEach(() => {
    trackEvent.mockClear();
  });

  it("links out safely with campaign attribution", () => {
    render(<Footer />);

    const link = screen.getByRole("link", { name: "Saransh" });
    expect(link).toHaveAttribute("href", SARANSH_FOOTER_URL);
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");
  });

  it("fires nav_click and saransh_click once each on click", () => {
    render(<Footer />);

    fireEvent.click(screen.getByRole("link", { name: "Saransh" }));

    expect(trackEvent).toHaveBeenCalledTimes(2);
    expect(trackEvent).toHaveBeenCalledWith("nav_click", {
      link_text: "Saransh",
      link_url: SARANSH_URL,
      nav_section: "footer",
    });
    expect(trackEvent).toHaveBeenCalledWith("saransh_click", {
      link_url: SARANSH_FOOTER_URL,
      page_location: "footer",
      placement: "footer",
    });
  });

  it("counts middle-click new-tab opens but ignores right-click", () => {
    render(<Footer />);

    const link = screen.getByRole("link", { name: "Saransh" });

    fireEvent(
      link,
      new MouseEvent("auxclick", {
        bubbles: true,
        cancelable: true,
        button: 2,
      }),
    );
    expect(trackEvent).not.toHaveBeenCalled();

    fireEvent(
      link,
      new MouseEvent("auxclick", {
        bubbles: true,
        cancelable: true,
        button: 1,
      }),
    );
    expect(trackEvent).toHaveBeenCalledTimes(2);
  });
});
