'use strict';
/**
 * dom-snapshot.js
 * Lightweight in-memory mock DOM utilities for property-based tests.
 *
 * No real browser, no jsdom, no Playwright.
 * Elements are plain JS objects with enough interface to support querySelectorAll,
 * classList inspection, and attribute access — sufficient for CSS property tests.
 */

// ---------------------------------------------------------------------------
// MockElement
// ---------------------------------------------------------------------------

/**
 * A minimal mock of a DOM element.
 * Supports classList, attributes, tagName, children, and innerText.
 */
class MockElement {
  /**
   * @param {string}   tagName
   * @param {string[]} classes
   * @param {Record<string, string>} [attrs]
   * @param {MockElement[]} [children]
   */
  constructor(tagName, classes = [], attrs = {}, children = []) {
    this.tagName    = tagName.toUpperCase();
    this.classList  = new MockClassList(classes);
    this.attributes = { ...attrs };
    this.children   = [...children];
    this.innerText  = '';
  }

  /**
   * getAttribute — mirrors the DOM API.
   * @param {string} name
   * @returns {string|null}
   */
  getAttribute(name) {
    return Object.prototype.hasOwnProperty.call(this.attributes, name)
      ? String(this.attributes[name])
      : null;
  }

  /**
   * A convenience accessor matching the DOM property.
   * @returns {string}
   */
  get className() {
    return this.classList.value;
  }
}

// ---------------------------------------------------------------------------
// MockClassList
// ---------------------------------------------------------------------------

/**
 * Minimal classList implementation.
 */
class MockClassList {
  /** @param {string[]} classes */
  constructor(classes) {
    this._classes = new Set(classes);
  }

  /** @returns {string} */
  get value() {
    return Array.from(this._classes).join(' ');
  }

  /**
   * @param {...string} tokens
   * @returns {boolean}
   */
  contains(...tokens) {
    return tokens.every((t) => this._classes.has(t));
  }

  /** @param {...string} tokens */
  add(...tokens) {
    tokens.forEach((t) => this._classes.add(t));
  }

  /** @param {...string} tokens */
  remove(...tokens) {
    tokens.forEach((t) => this._classes.delete(t));
  }

  /** @returns {string[]} */
  values() {
    return Array.from(this._classes);
  }

  /** @returns {IterableIterator<string>} */
  [Symbol.iterator]() {
    return this._classes[Symbol.iterator]();
  }
}

// ---------------------------------------------------------------------------
// MockDocument
// ---------------------------------------------------------------------------

/**
 * Minimal mock document with a querySelectorAll implementation.
 */
class MockDocument {
  /** @param {MockElement} rootElement */
  constructor(rootElement) {
    this._root = rootElement;
  }

  /**
   * querySelectorAll — supports a restricted but sufficient subset of CSS selectors:
   *   - Tag selectors:           "h1", "p", "span" …
   *   - Class selectors:         ".shell-card", ".badge" …
   *   - Multi-class selectors:   ".shell-card.badge" (AND)
   *   - Attribute selectors:     "[data-role]" (presence only)
   *   - Descendant combinator:   "div .badge"
   *
   * @param {string} selector
   * @returns {MockElement[]}
   */
  querySelectorAll(selector) {
    return matchAll(this._root, selector.trim());
  }

  /**
   * querySelector — returns the first match or null.
   * @param {string} selector
   * @returns {MockElement|null}
   */
  querySelector(selector) {
    const results = this.querySelectorAll(selector);
    return results.length > 0 ? results[0] : null;
  }
}

// ---------------------------------------------------------------------------
// Selector matching engine
// ---------------------------------------------------------------------------

/**
 * Collect all descendants of `root` (including root itself) that match `selector`.
 * @param {MockElement} root
 * @param {string}      selector
 * @returns {MockElement[]}
 */
function matchAll(root, selector) {
  const all = flattenTree(root);

  // Handle descendant combinator (space-separated parts).
  const parts = selector.split(/\s+/);

  if (parts.length === 1) {
    return all.filter((el) => matchesSimple(el, parts[0]));
  }

  // For descendant selectors we apply a simple left-to-right filter.
  // Collect all elements matching the first part, then find descendants matching
  // subsequent parts. This covers common test patterns like "div .badge".
  let candidates = all.filter((el) => matchesSimple(el, parts[0]));
  for (let i = 1; i < parts.length; i++) {
    const part = parts[i];
    const nextCandidates = [];
    for (const ancestor of candidates) {
      flattenTree(ancestor)
        .slice(1) // exclude ancestor itself
        .filter((el) => matchesSimple(el, part))
        .forEach((el) => nextCandidates.push(el));
    }
    candidates = nextCandidates;
  }
  return candidates;
}

/**
 * Return `true` if `el` matches a *simple* selector token (no combinators).
 * Supports:
 *   - "*"
 *   - "tagname"
 *   - ".className" (or ".class1.class2" for AND)
 *   - "[attribute]" (presence check)
 *   - "tag.className"
 *
 * @param {MockElement} el
 * @param {string}      simple
 * @returns {boolean}
 */
function matchesSimple(el, simple) {
  if (simple === '*') return true;

  let remaining = simple;

  // Extract tag part (if any — stops at '.' or '[').
  const tagMatch = remaining.match(/^([a-zA-Z][a-zA-Z0-9-]*)/);
  if (tagMatch) {
    if (el.tagName !== tagMatch[1].toUpperCase()) return false;
    remaining = remaining.slice(tagMatch[1].length);
  }

  // Extract class tokens.
  const classTokens = remaining.match(/\.[a-zA-Z_-][a-zA-Z0-9_-]*/g) || [];
  for (const token of classTokens) {
    const cls = token.slice(1); // remove leading '.'
    if (!el.classList.contains(cls)) return false;
  }

  // Extract attribute presence tokens.
  const attrTokens = remaining.match(/\[([^\]]+)\]/g) || [];
  for (const token of attrTokens) {
    const attrName = token.slice(1, -1).trim();
    if (el.getAttribute(attrName) === null) return false;
  }

  return true;
}

/**
 * Flatten a MockElement tree (depth-first) into a flat array.
 * @param {MockElement} el
 * @returns {MockElement[]}
 */
function flattenTree(el) {
  const result = [el];
  for (const child of el.children) {
    flattenTree(child).forEach((c) => result.push(c));
  }
  return result;
}

// ---------------------------------------------------------------------------
// Factory: createMockDOM
// ---------------------------------------------------------------------------

/**
 * @typedef {Object} MockDOMConfig
 * @property {number} [shellCards=3]   Number of .shell-card elements to include.
 * @property {number} [badges=4]       Number of .badge elements (inside shell-cards).
 * @property {number} [headings=2]     Number of heading elements (h1–h4).
 * @property {number} [gridItems=6]    Number of generic grid child elements.
 * @property {string[]} [extraClasses] Additional classes to add to the body element.
 */

/**
 * createMockDOM
 * Creates an in-memory mock DOM structure with configurable counts of
 * `.shell-card`, `.badge`, heading, and grid elements.
 *
 * Returns an object that exposes `querySelectorAll(selector)` and
 * `querySelector(selector)` methods, matching the DOM API enough for
 * all property-based tests in this suite.
 *
 * @param {MockDOMConfig} [config]
 * @returns {MockDocument}
 */
function createMockDOM(config = {}) {
  const {
    shellCards  = 3,
    badges      = 4,
    headings    = 2,
    gridItems   = 6,
    extraClasses = [],
  } = config;

  // ── Heading elements ───────────────────────────────────────────────────
  const headingTags  = ['h1', 'h2', 'h3', 'h4'];
  const headingNodes = Array.from({ length: headings }, (_, i) => {
    const tag = headingTags[i % headingTags.length];
    const el  = new MockElement(tag, ['heading']);
    el.innerText = `Heading ${i + 1}`;
    return el;
  });

  // ── Badge elements (standalone, not inside shell-cards) ────────────────
  const badgeVariants = [
    'badge--green',
    'badge--blue',
    'badge--orange',
    'badge--red',
    'badge--accent',
    'badge--outline',
  ];
  const standaloneBadges = Array.from({ length: badges }, (_, i) => {
    const variant = badgeVariants[i % badgeVariants.length];
    return new MockElement('span', ['badge', variant]);
  });

  // ── Shell-card elements (each with a badge child and content) ──────────
  const shellCardNodes = Array.from({ length: shellCards }, (_, i) => {
    const badgeVariant = badgeVariants[i % badgeVariants.length];
    const badge = new MockElement('span', ['badge', badgeVariant]);

    const header = new MockElement('div', ['card-header-gradient'], {}, [badge]);
    const body   = new MockElement('div', ['card-body']);

    return new MockElement('div', ['shell-card'], {}, [header, body]);
  });

  // ── Grid elements ──────────────────────────────────────────────────────
  const gridNode = new MockElement(
    'div',
    ['stats-grid'],
    {},
    Array.from({ length: gridItems }, (_, i) => {
      const icon  = new MockElement('div', ['stat-card-icon']);
      const value = new MockElement('span', ['stat-card-value']);
      const label = new MockElement('span', ['stat-card-label']);
      value.innerText = String((i + 1) * 100);
      label.innerText = `Stat ${i + 1}`;
      return new MockElement('div', ['stat-card'], {}, [icon, value, label]);
    })
  );

  // ── Filter toolbar ─────────────────────────────────────────────────────
  const filterChips = Array.from({ length: 3 }, (_, i) => {
    const classes = ['filter-chip'];
    if (i === 0) classes.push('active');
    return new MockElement('button', classes);
  });
  const filterToolbar = new MockElement('div', ['filter-toolbar'], {}, filterChips);

  // ── Root body element ──────────────────────────────────────────────────
  const bodyClasses = ['page-body', ...extraClasses];
  const body = new MockElement(
    'div',
    bodyClasses,
    {},
    [
      ...headingNodes,
      ...standaloneBadges,
      ...shellCardNodes,
      gridNode,
      filterToolbar,
    ]
  );

  return new MockDocument(body);
}

// ---------------------------------------------------------------------------
// Exports
// ---------------------------------------------------------------------------

module.exports = {
  MockElement,
  MockClassList,
  MockDocument,
  createMockDOM,
};
