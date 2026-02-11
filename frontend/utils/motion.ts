/**
 * Motion Animation Variants and Utilities
 * Reusable animation configurations for Framer Motion
 */

export const fadeIn = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
}

export const fadeInUp = {
    initial: { opacity: 0, y: 60 },
    animate: { opacity: 1, y: 0 },
}

export const fadeInDown = {
    initial: { opacity: 0, y: -60 },
    animate: { opacity: 1, y: 0 },
}

export const scaleIn = {
    initial: { opacity: 0, scale: 0.8 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.8 },
}

export const slideInLeft = {
    initial: { opacity: 0, x: -60 },
    animate: { opacity: 1, x: 0 },
}

export const slideInRight = {
    initial: { opacity: 0, x: 60 },
    animate: { opacity: 1, x: 0 },
}

// Container for staggered children
export const staggerContainer = {
    initial: {},
    animate: {
        transition: {
            staggerChildren: 0.1,
            delayChildren: 0.2,
        },
    },
}

// Fast stagger for grids
export const staggerFastContainer = {
    initial: {},
    animate: {
        transition: {
            staggerChildren: 0.05,
        },
    },
}

// Card hover effect
export const cardHover = {
    rest: { scale: 1, y: 0 },
    hover: { 
        scale: 1.02, 
        y: -4,
        transition: {
            duration: 0.3,
            ease: "easeOut"
        }
    },
}

// Button press effect
export const buttonTap = {
    scale: 0.95,
}

// Transition presets
export const springTransition = {
    type: "spring" as const,
    stiffness: 260,
    damping: 20,
}

export const smoothTransition = {
    duration: 0.5,
    ease: "easeOut" as const,
}

export const quickTransition = {
    duration: 0.3,
    ease: "easeOut" as const,
}

// Scroll-triggered animations
export const scrollReveal = {
    initial: { opacity: 0, y: 50 },
    whileInView: { opacity: 1, y: 0 },
    viewport: { once: true, amount: 0.3 },
    transition: smoothTransition,
}

export const scrollRevealLeft = {
    initial: { opacity: 0, x: -50 },
    whileInView: { opacity: 1, x: 0 },
    viewport: { once: true, amount: 0.3 },
    transition: smoothTransition,
}

export const scrollRevealRight = {
    initial: { opacity: 0, x: 50 },
    whileInView: { opacity: 1, x: 0 },
    viewport: { once: true, amount: 0.3 },
    transition: smoothTransition,
}

// Entrance animations for pages
export const pageTransition = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 20 },
    transition: smoothTransition,
}
