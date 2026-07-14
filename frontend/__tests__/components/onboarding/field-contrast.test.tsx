import { fireEvent, render, screen } from "@testing-library/react";
import UserDetailsStep from "@/components/onboarding/UserDetailsStep";
import UsernameStep from "@/components/onboarding/UsernameStep";

// After the Sutra migration, fields are styled with token-driven utilities
// (bg-surface / text-content / placeholder:text-content-subtle) that flip
// automatically in dark mode — the guarantee these tests protect.
describe("onboarding field contrast styles", () => {
  it("applies token-driven field styles to basic detail inputs and state select", () => {
    const onChange = jest.fn();

    render(
      <UserDetailsStep
        formData={{ phone: "", state: "", city: "", age_group: "" }}
        onChange={onChange}
      />,
    );

    const phoneInput = screen.getByPlaceholderText("+91-9876543210");
    const cityInput = screen.getByPlaceholderText("Enter your city");
    const stateSelect = screen.getByRole("combobox");

    expect(phoneInput).toHaveClass(
      "bg-surface",
      "text-content",
      "placeholder:text-content-subtle",
    );
    expect(cityInput).toHaveClass(
      "bg-surface",
      "text-content",
      "placeholder:text-content-subtle",
    );
    // Empty state is tinted subtle; base text-content is merged into it.
    expect(stateSelect).toHaveClass("bg-surface", "text-content-subtle");

    fireEvent.change(stateSelect, { target: { value: "Delhi" } });
    expect(onChange).toHaveBeenCalledWith("state", "Delhi");
  });

  it("applies token-driven styles to the username input", () => {
    render(
      <UsernameStep value="" onChange={jest.fn()} onValidation={jest.fn()} />,
    );

    expect(screen.getByPlaceholderText("johndoe")).toHaveClass(
      "bg-surface",
      "text-content",
      "placeholder:text-content-subtle",
    );
  });
});
