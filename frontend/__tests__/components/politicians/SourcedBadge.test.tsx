import { render, screen } from "@testing-library/react";

import SourcedBadge, {
  getSourcedBadgeState,
} from "@/components/politicians/SourcedBadge";

function renderBadge(overrides?: {
  sourced_pct?: number | null;
  cited_fields_count?: number | null;
  checkable_fields_count?: number | null;
}) {
  return render(
    <SourcedBadge
      politician={{
        sourced_pct: null,
        cited_fields_count: null,
        checkable_fields_count: null,
        ...overrides,
      }}
    />,
  );
}

describe("getSourcedBadgeState", () => {
  it("hides when sourcing metrics are unavailable", () => {
    expect(getSourcedBadgeState({})).toEqual({ kind: "hidden" });
  });
});

describe("SourcedBadge", () => {
  it("renders limited data when fewer than three fields are checkable", () => {
    renderBadge({ sourced_pct: 1, cited_fields_count: 2, checkable_fields_count: 2 });

    const badge = screen.getByText("Limited data").closest("[data-sourced-band]");
    expect(badge).toHaveAttribute("data-sourced-state", "limited");
    expect(badge).toHaveAttribute("data-sourced-band", "neutral");
  });

  it("renders the unverified copy for genuine zero coverage", () => {
    renderBadge({ sourced_pct: 0, cited_fields_count: 0, checkable_fields_count: 3 });

    const badge = screen
      .getByText("Unverified — help us source this")
      .closest("[data-sourced-band]");
    expect(badge).toHaveAttribute("data-sourced-state", "unverified");
    expect(badge).toHaveAttribute("data-sourced-band", "red");
  });

  it("uses the red band below the 0.60 boundary even when the display rounds up", () => {
    renderBadge({
      sourced_pct: 0.599,
      cited_fields_count: 599,
      checkable_fields_count: 1000,
    });

    const badge = screen
      .getByText("Low coverage · 60% sourced")
      .closest("[data-sourced-band]");
    expect(badge).toHaveAttribute("data-sourced-band", "red");
  });

  it("uses the yellow band at the 0.60 boundary", () => {
    renderBadge({
      sourced_pct: 0.6,
      cited_fields_count: 3,
      checkable_fields_count: 5,
    });

    const badge = screen
      .getByText("Medium coverage · 60% sourced")
      .closest("[data-sourced-band]");
    expect(badge).toHaveAttribute("data-sourced-band", "yellow");
  });

  it("stays yellow at the 0.749 boundary while rounding the display only", () => {
    renderBadge({
      sourced_pct: 0.749,
      cited_fields_count: 749,
      checkable_fields_count: 1000,
    });

    const badge = screen
      .getByText("Medium coverage · 75% sourced")
      .closest("[data-sourced-band]");
    expect(badge).toHaveAttribute("data-sourced-band", "yellow");
  });

  it("uses the green band at the 0.75 boundary", () => {
    renderBadge({
      sourced_pct: 0.75,
      cited_fields_count: 3,
      checkable_fields_count: 4,
    });

    const badge = screen
      .getByText("High coverage · 75% sourced")
      .closest("[data-sourced-band]");
    expect(badge).toHaveAttribute("data-sourced-band", "green");
  });
});
