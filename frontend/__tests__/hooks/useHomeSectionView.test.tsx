import { renderHook } from "@testing-library/react";
import { StrictMode, useRef } from "react";
import { useHomeSectionView } from "@/hooks/useHomeSectionView";

const trackEvent = jest.fn();

jest.mock("@/hooks/useAnalytics", () => ({
  useAnalytics: () => ({ trackEvent }),
}));

type ObserverCallback = (entries: Array<{ isIntersecting: boolean }>) => void;

const observe = jest.fn();
const disconnect = jest.fn();
let callbacks: ObserverCallback[] = [];

class MockIntersectionObserver {
  constructor(
    callback: ObserverCallback,
    public options?: IntersectionObserverInit,
  ) {
    callbacks.push(callback);
    observers.push(this);
    this.options = options;
  }
  observe = observe;
  disconnect = disconnect;
  unobserve = jest.fn();
  takeRecords = jest.fn();
}

let observers: MockIntersectionObserver[] = [];

function renderSectionHook() {
  return renderHook(() => {
    const ref = useRef<HTMLElement>(document.createElement("section"));
    useHomeSectionView(ref, "saransh");
  });
}

describe("useHomeSectionView", () => {
  beforeEach(() => {
    callbacks = [];
    observers = [];
    trackEvent.mockClear();
    observe.mockClear();
    disconnect.mockClear();
    (
      window as unknown as { IntersectionObserver: unknown }
    ).IntersectionObserver = MockIntersectionObserver;
    (
      globalThis as unknown as { IntersectionObserver: unknown }
    ).IntersectionObserver = MockIntersectionObserver;
  });

  it("observes the section at a 50 % threshold", () => {
    renderSectionHook();

    expect(observe).toHaveBeenCalledTimes(1);
    expect(observers[0].options).toEqual({ threshold: 0.5 });
    expect(trackEvent).not.toHaveBeenCalled();
  });

  it("fires home_section_view once when the section becomes visible", () => {
    renderSectionHook();

    callbacks[0]([{ isIntersecting: true }]);
    callbacks[0]([{ isIntersecting: true }]);

    expect(trackEvent).toHaveBeenCalledTimes(1);
    expect(trackEvent).toHaveBeenCalledWith("home_section_view", {
      section_name: "saransh",
    });
  });

  it("does not fire while the section is out of view", () => {
    renderSectionHook();

    callbacks[0]([{ isIntersecting: false }]);

    expect(trackEvent).not.toHaveBeenCalled();
  });

  it("disconnects the observer on unmount", () => {
    const { unmount } = renderSectionHook();

    unmount();

    expect(disconnect).toHaveBeenCalled();
  });

  it("fires only once under React strict mode's double effect run", () => {
    renderHook(
      () => {
        const ref = useRef<HTMLElement>(document.createElement("section"));
        useHomeSectionView(ref, "saransh");
      },
      { wrapper: StrictMode },
    );

    callbacks.forEach((fire) => fire([{ isIntersecting: true }]));

    expect(trackEvent).toHaveBeenCalledTimes(1);
  });
});
