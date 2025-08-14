---
author: Framework Team
date: '2025-01-20'
slug: 2025-01-20-documentation-latex-math-rendering-test
slug_locked: true
slug_source: creation_context
summary: Testing mathematical formula rendering with KaTeX
title: LaTeX Math Rendering Test
type: documentation
---

# LaTeX Math Rendering Test

This document tests the LaTeX math rendering capabilities using KaTeX. All mathematical expressions should render beautifully with proper typography.

## Inline Math Examples

Here are some inline math expressions:

- The quadratic formula: $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$
- Einstein's mass-energy equivalence: $E = mc^2$
- The derivative of $f(x) = x^2$ is $f'(x) = 2x$
- A simple fraction: $\frac{1}{2} + \frac{1}{3} = \frac{5}{6}$
- Greek letters: $\alpha, \beta, \gamma, \Delta, \Omega$
- Subscripts and superscripts: $x_1^2 + x_2^2 = r^2$

## Block Math Examples

### Basic Algebra

$$
\begin{align}
(x + y)^2 &= x^2 + 2xy + y^2 \\
(x - y)^2 &= x^2 - 2xy + y^2 \\
x^2 - y^2 &= (x + y)(x - y)
\end{align}
$$

### Calculus

The fundamental theorem of calculus:

$$
\int_a^b f'(x) \, dx = f(b) - f(a)
$$

Derivative of exponential function:

$$
\frac{d}{dx} e^x = e^x
$$

Integration by parts:

$$
\int u \, dv = uv - \int v \, du
$$

### Linear Algebra

Matrix multiplication (single line):

$$\begin{pmatrix} a & b \\ c & d \end{pmatrix} \begin{pmatrix} e & f \\ g & h \end{pmatrix} = \begin{pmatrix} ae + bg & af + bh \\ ce + dg & cf + dh \end{pmatrix}$$



Alternative with brackets:

$$\begin{bmatrix} a & b \\ c & d \end{bmatrix} \begin{bmatrix} e & f \\ g & h \end{bmatrix} = \begin{bmatrix} ae + bg & af + bh \\ ce + dg & cf + dh \end{bmatrix}$$

Determinant of a 2×2 matrix:

$$
\det \begin{pmatrix} a & b \\ c & d \end{pmatrix} = ad - bc
$$

### Complex Expressions

The quadratic formula:

$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$

Euler's identity:

$$
e^{i\pi} + 1 = 0
$$

Summation notation:

$$
\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}
$$

### Probability and Statistics

Normal distribution:

$$
f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}
$$

Bayes' theorem:

$$
P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)}
$$

## Test Results

If you can see properly formatted mathematical expressions above, then KaTeX is working correctly. All formulas should render with:

- Proper mathematical typography
- Correctly sized fractions and symbols
- Proper spacing and alignment
- Clear matrix and vector notation

## Troubleshooting

If math is not rendering:

1. Check that KaTeX CSS and JavaScript are loaded
2. Verify that the math rendering module is initialized
3. Check browser console for errors
4. Ensure Hugo's math passthrough is enabled 