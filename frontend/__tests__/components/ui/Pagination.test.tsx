import { render, screen, fireEvent } from "@testing-library/react";
import Pagination, { computePageRange } from "@/components/ui/Pagination";

// Mock next/link to render a simple anchor for testing
jest.mock("next/link", () => {
  return function MockLink({
    href,
    children,
    ...props
  }: {
    href: string;
    children: React.ReactNode;
    className?: string;
    "aria-label"?: string;
  }) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    );
  };
});

describe("computePageRange", () => {
  it("returns all pages for small page counts", () => {
    expect(computePageRange(1, 5, 1)).toEqual([1, 2, 3, 4, 5]);
    expect(computePageRange(3, 7, 2)).toEqual([1, 2, 3, 4, 5, 6, 7]);
  });

  it("shows ellipsis on the right for first pages", () => {
    const result = computePageRange(1, 20, 1);
    expect(result[0]).toBe(1);
    expect(result[1]).toBe(2);
    expect(result).toContain("…");
    expect(result[result.length - 1]).toBe(20);
  });

  it("shows ellipsis on the left for last pages", () => {
    const result = computePageRange(20, 20, 1);
    expect(result[0]).toBe(1);
    expect(result).toContain("…");
    expect(result[result.length - 2]).toBe(19);
    expect(result[result.length - 1]).toBe(20);
  });

  it("shows ellipsis on both sides for middle pages", () => {
    const result = computePageRange(10, 20, 1);
    expect(result[0]).toBe(1);
    expect(result[1]).toBe("…");
    expect(result).toContain(9);
    expect(result).toContain(10);
    expect(result).toContain(11);
    expect(result[result.length - 2]).toBe("…");
    expect(result[result.length - 1]).toBe(20);
  });

  it("always includes first and last page", () => {
    const result = computePageRange(50, 90, 2);
    expect(result[0]).toBe(1);
    expect(result[result.length - 1]).toBe(90);
  });

  it("shows current page with correct siblings", () => {
    const result = computePageRange(50, 90, 2);
    expect(result).toContain(48);
    expect(result).toContain(49);
    expect(result).toContain(50);
    expect(result).toContain(51);
    expect(result).toContain(52);
  });
});

describe("Pagination Component", () => {
  it("renders nothing when totalPages is 1", () => {
    const { container } = render(
      <Pagination currentPage={1} totalPages={1} />
    );
    expect(container.firstChild).toBeNull();
  });

  it("renders pagination nav with proper aria label", () => {
    render(<Pagination currentPage={1} totalPages={10} />);
    expect(screen.getByRole("navigation")).toHaveAttribute(
      "aria-label",
      "Pagination"
    );
  });

  it("marks the current page with aria-current", () => {
    render(<Pagination currentPage={5} totalPages={10} />);
    // Current page appears in both mobile and desktop views
    const currentPageElements = screen.getAllByText("5");
    expect(currentPageElements.length).toBeGreaterThanOrEqual(1);
    currentPageElements.forEach((el) => {
      expect(el).toHaveAttribute("aria-current", "page");
    });
  });

  it("disables Previous button on first page", () => {
    render(<Pagination currentPage={1} totalPages={10} />);
    const prevButton = screen.getByLabelText(
      /Previous page.*disabled.*first page/i
    );
    expect(prevButton).toHaveAttribute("aria-disabled", "true");
  });

  it("disables Next button on last page", () => {
    render(<Pagination currentPage={10} totalPages={10} />);
    const nextButton = screen.getByLabelText(
      /Next page.*disabled.*last page/i
    );
    expect(nextButton).toHaveAttribute("aria-disabled", "true");
  });

  it("renders links when buildHref is provided", () => {
    render(
      <Pagination
        currentPage={5}
        totalPages={10}
        buildHref={(page) => `/page/${page}`}
      />
    );
    
    // Check that page 1 links exist (in both mobile and desktop views)
    const page1Links = screen.getAllByRole("link", { name: "Go to page 1" });
    expect(page1Links.length).toBeGreaterThanOrEqual(1);
    page1Links.forEach((link) => {
      expect(link).toHaveAttribute("href", "/page/1");
    });
    
    // Check that Previous links exist
    const prevLinks = screen.getAllByRole("link", { name: "Go to previous page" });
    expect(prevLinks.length).toBeGreaterThanOrEqual(1);
    prevLinks.forEach((link) => {
      expect(link).toHaveAttribute("href", "/page/4");
    });
    
    // Check that Next links exist
    const nextLinks = screen.getAllByRole("link", { name: "Go to next page" });
    expect(nextLinks.length).toBeGreaterThanOrEqual(1);
    nextLinks.forEach((link) => {
      expect(link).toHaveAttribute("href", "/page/6");
    });
  });

  it("calls onPageChange when a page button is clicked", () => {
    const handlePageChange = jest.fn();
    render(
      <Pagination
        currentPage={5}
        totalPages={10}
        onPageChange={handlePageChange}
      />
    );
    
    // Click on page 1 (there may be multiple, click the first one)
    const page1Buttons = screen.getAllByRole("button", { name: "Go to page 1" });
    fireEvent.click(page1Buttons[0]);
    expect(handlePageChange).toHaveBeenCalledWith(1);
    
    // Click on Next button (there's only one)
    const nextButton = screen.getByRole("button", { name: "Go to next page" });
    fireEvent.click(nextButton);
    expect(handlePageChange).toHaveBeenCalledWith(6);
    
    // Click on Previous button (there's only one)
    const prevButton = screen.getByRole("button", { name: "Go to previous page" });
    fireEvent.click(prevButton);
    expect(handlePageChange).toHaveBeenCalledWith(4);
  });

  it("renders page numbers and ellipsis correctly", () => {
    render(<Pagination currentPage={50} totalPages={90} />);
    
    // First and last page should always be visible (multiple instances due to mobile/desktop)
    const ones = screen.getAllByText("1");
    expect(ones.length).toBeGreaterThanOrEqual(1);
    
    const nineties = screen.getAllByText("90");
    expect(nineties.length).toBeGreaterThanOrEqual(1);
    
    // Ellipsis should be present
    const ellipses = screen.getAllByText("…");
    expect(ellipses.length).toBeGreaterThanOrEqual(2);
    
    // Current page should be visible
    const fifties = screen.getAllByText("50");
    expect(fifties.length).toBeGreaterThanOrEqual(1);
  });

  it("has responsive mobile and desktop views", () => {
    const { container } = render(
      <Pagination currentPage={50} totalPages={90} />
    );
    
    // Check for sm:hidden (mobile) and hidden sm:flex (desktop) classes
    const mobileContainer = container.querySelector(".sm\\:hidden");
    const desktopContainer = container.querySelector(".hidden.sm\\:flex");
    
    expect(mobileContainer).toBeInTheDocument();
    expect(desktopContainer).toBeInTheDocument();
  });

  it("applies custom className to nav wrapper", () => {
    render(
      <Pagination
        currentPage={1}
        totalPages={10}
        className="custom-class"
      />
    );
    expect(screen.getByRole("navigation")).toHaveClass("custom-class");
  });
});
