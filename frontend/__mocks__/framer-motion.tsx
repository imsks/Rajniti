import React from "react";

type MotionProps = React.PropsWithChildren<Record<string, unknown>>;

function makeMotionComponent(tag: keyof JSX.IntrinsicElements) {
  return ({ children, ...props }: MotionProps) =>
    React.createElement(tag, props, children);
}

const motionComponents = {
  div: makeMotionComponent("div"),
  section: makeMotionComponent("section"),
  button: makeMotionComponent("button"),
  span: makeMotionComponent("span"),
  svg: makeMotionComponent("svg"),
  h1: makeMotionComponent("h1"),
  h2: makeMotionComponent("h2"),
  p: makeMotionComponent("p"),
  ul: makeMotionComponent("ul"),
  li: makeMotionComponent("li"),
  a: makeMotionComponent("a"),
  img: makeMotionComponent("img"),
};

export const m = motionComponents;
export const motion = motionComponents;

export function AnimatePresence({ children }: MotionProps) {
  return <>{children}</>;
}

export function LazyMotion({ children }: MotionProps) {
  return <>{children}</>;
}

export const domAnimation = {};
