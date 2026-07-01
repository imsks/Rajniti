import { render, screen } from "@testing-library/react";

import SourcedBadge, {
  getSourcedBadgeState,
} from "@/components/politicians/SourcedBadge";

function renderBadge(overrides?: {
  sourced_pct?: number | null;
  cited_fields_count?: number | null;
  checkable_fields_count?: number | null;
  categories_mostly_present?: boolean | null;
}) {
  return render(
    <SourcedBadge
      politician={{
        sourced_pct: null,
        cited_fields_count: null,
        checkable_fields_count: null,
        categories_mostly_present: null,
        ...overrides,
      }}
    />,
  );
}

describe("getSourcedBadgeState", () => {
  it("falls back to limited data when sourcing metrics are unavailable", () => {
    expect(getSourcedBadgeState({})).toEqual({
      kind: "limited",
      band: "blue",
      label: "Limited data",
    });
  });
});

describe("SourcedBadge", () => {
  it("always renders a badge, even with no data at all", () => {
    renderBadge();
    expect(screen.getByText("Limited data")).toBeInTheDocument();
  });

  it("renders limited data when there are no checkable fields at all", () => {
    renderBadge({ sourced_pct: null, cited_fields_count: 0, checkable_fields_count: 0 });

    const badge = screen.getByText("Limited data").closest("[data-sourced-band]");
    expect(badge).toHaveAttribute("data-sourced-state", "limited");
    expect(badge).toHaveAttribute("data-sourced-band", "blue");
  });

  it("renders unverified for a single uncited fact, even with just one category present", () => {
    renderBadge({
      sourced_pct: 0,
      cited_fields_count: 0,
      checkable_fields_count: 1,
      categories_mostly_present: false,
    });

    const badge = screen
      .getByText("Unverified — help us source this")
      .closest("[data-sourced-band]");
    expect(badge).toHaveAttribute("data-sourced-state", "unverified");
    expect(badge).toHaveAttribute("data-sourced-band", "red");
  });

  it("renders unverified when every category has exactly one uncited fact", () => {
    renderBadge({
      sourced_pct: 0,
      cited_fields_count: 0,
      checkable_fields_count: 5,
      categories_mostly_present: true,
    });

    const badge = screen
      .getByText("Unverified — help us source this")
      .closest("[data-sourced-band]");
    expect(badge).toHaveAttribute("data-sourced-state", "unverified");
  });

  it("renders limited data when some facts are cited but not every category has data yet", () => {
    renderBadge({
      sourced_pct: 1,
      cited_fields_count: 2,
      checkable_fields_count: 2,
      categories_mostly_present: false,
    });

    const badge = screen.getByText("Limited data").closest("[data-sourced-band]");
    expect(badge).toHaveAttribute("data-sourced-state", "limited");
    expect(badge).toHaveAttribute("data-sourced-band", "blue");
  });

  it("renders limited data when every category has data but the total is still under five", () => {
    renderBadge({
      sourced_pct: 0.75,
      cited_fields_count: 3,
      checkable_fields_count: 4,
      categories_mostly_present: true,
    });

    const badge = screen.getByText("Limited data").closest("[data-sourced-band]");
    expect(badge).toHaveAttribute("data-sourced-state", "limited");
  });

  it("uses the red band below the 0.60 boundary even when the display rounds up", () => {
    renderBadge({
      sourced_pct: 0.599,
      cited_fields_count: 599,
      checkable_fields_count: 1000,
      categories_mostly_present: true,
    });

    const badge = screen
      .getByText("60% verified · Low")
      .closest("[data-sourced-band]");
    expect(badge).toHaveAttribute("data-sourced-band", "red");
  });

  it("uses the yellow band at the 0.60 boundary", () => {
    renderBadge({
      sourced_pct: 0.6,
      cited_fields_count: 3,
      checkable_fields_count: 5,
      categories_mostly_present: true,
    });

    const badge = screen
      .getByText("60% verified · Medium")
      .closest("[data-sourced-band]");
    expect(badge).toHaveAttribute("data-sourced-band", "yellow");
  });

  it("stays yellow at the 0.749 boundary while rounding the display only", () => {
    renderBadge({
      sourced_pct: 0.749,
      cited_fields_count: 749,
      checkable_fields_count: 1000,
      categories_mostly_present: true,
    });

    const badge = screen
      .getByText("75% verified · Medium")
      .closest("[data-sourced-band]");
    expect(badge).toHaveAttribute("data-sourced-band", "yellow");
  });

  it("uses the green band at the 0.75 boundary", () => {
    renderBadge({
      sourced_pct: 0.75,
      cited_fields_count: 3,
      checkable_fields_count: 5,
      categories_mostly_present: true,
    });

    const badge = screen
      .getByText("75% verified · High")
      .closest("[data-sourced-band]");
    expect(badge).toHaveAttribute("data-sourced-band", "green");
  });
});
