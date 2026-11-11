#!/usr/bin/env python3
"""Inline LaTeX -> plain Unicode text for slide copies.

Used by build_pptx.py (the direct python-pptx engine writes no OMML) and by
md_to_slides.py. Only a small, documented subset is mapped; anything else is
reported through the `unmapped` list so the caller can warn. The markdown source
keeps its TeX; only the slide text is flattened.
"""
import re

SYMBOLS = {
    # Greek
    'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ', 'epsilon': 'ε', 'varepsilon': 'ε',
    'zeta': 'ζ', 'eta': 'η', 'theta': 'θ', 'lambda': 'λ', 'mu': 'μ', 'nu': 'ν', 'xi': 'ξ',
    'pi': 'π', 'rho': 'ρ', 'sigma': 'σ', 'tau': 'τ', 'phi': 'φ', 'varphi': 'φ', 'chi': 'χ',
    'psi': 'ψ', 'omega': 'ω',
    'Gamma': 'Γ', 'Delta': 'Δ', 'Theta': 'Θ', 'Lambda': 'Λ', 'Xi': 'Ξ', 'Pi': 'Π',
    'Sigma': 'Σ', 'Phi': 'Φ', 'Psi': 'Ψ', 'Omega': 'Ω',
    # operators / relations
    'sum': '∑', 'approx': '≈', 'times': '×', 'le': '≤', 'leq': '≤', 'ge': '≥', 'geq': '≥',
    'cdot': '·', 'pm': '±', 'to': '→', 'rightarrow': '→', 'leftarrow': '←',
    'leftrightarrow': '↔', 'infty': '∞', 'partial': '∂', 'sim': '~', 'neq': '≠', 'ne': '≠',
    'gtrsim': '≳', 'lesssim': '≲', 'nabla': '∇', 'int': '∫', 'prod': '∏', 'propto': '∝',
    'ldots': '…', 'dots': '…', 'langle': '⟨', 'rangle': '⟩',
}
FUNCTIONS = ('ln', 'log', 'exp', 'sin', 'cos', 'tan', 'min', 'max', 'lim', 'var', 'cov')
SUP = str.maketrans('0123456789+-=()ni', '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ')
SUB = str.maketrans('0123456789+-=()', '₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎')


def _script(m, table, mark):
    body = m.group(1) if m.group(1) is not None else m.group(2)
    mapped = body.translate(table)
    if all(c in {chr(v) for v in table.values()} | {' '} for c in mapped):
        return mapped
    return mark + (body if len(body) == 1 else '(' + body + ')')


def latex_to_text(expr, unmapped=None):
    """Convert one math expression (without the $ delimiters)."""
    t = expr
    t = re.sub(r'\\(?:mathrm|mathbf|mathit|text|textrm|operatorname|rm|bf)\s*\{([^{}]*)\}', r'\1', t)
    t = re.sub(r'\{\\(?:rm|bf|it)\s+([^{}]*)\}', r'\1', t)
    t = re.sub(r'\\[dt]?frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}', r'(\1)/(\2)', t)
    t = re.sub(r'\\sqrt\s*\{([^{}]*)\}', r'√(\1)', t)
    t = re.sub(r'\\(?:left|right|big|Big|bigg|Bigg)\s*([()\[\]|.]?)', lambda m: '' if m.group(1) == '.' else m.group(1), t)
    t = re.sub(r'\\(?:bar|hat|tilde|overline|vec)\s*\{([^{}]*)\}', r'\1', t)
    t = re.sub(r'\\(?:,|;|:|!|quad|qquad)\s*', ' ', t)
    t = re.sub(r'\\(' + '|'.join(FUNCTIONS) + r')(?![A-Za-z])\s*', r'\1 ', t)

    def sym(m):
        name = m.group(1)
        if name in SYMBOLS:
            return SYMBOLS[name]
        if unmapped is not None:
            unmapped.append('\\' + name)
        return ''
    t = re.sub(r'\\([A-Za-z]+)(?:[ ]+(?=[A-Za-z]))?', sym, t)
    t = re.sub(r'\^\{([^{}]*)\}|\^([A-Za-z0-9+\-])', lambda m: _script(m, SUP, '^'), t)
    t = re.sub(r'_\{([^{}]*)\}|_([A-Za-z0-9+\-])', lambda m: _script(m, SUB, '_'), t)
    t = t.replace('\\{', '{').replace('\\}', '}').replace('\\%', '%').replace('\\_', '_')
    t = t.replace('{', '').replace('}', '').replace('\\', '')
    return re.sub(r' {2,}', ' ', t).strip()


MATH_RE = re.compile(r'(?<![\\$])\$(?!\s)([^$\n]+?)(?<!\s)\$(?!\d)')


def convert_math(text, unmapped=None):
    """Replace every inline $...$ in `text` with its plain-text form."""
    return MATH_RE.sub(lambda m: latex_to_text(m.group(1), unmapped), text)
