'use strict';
/**
 * css-parser.js
 * Pure Node.js CSS text-parsing utilities for property-based tests.
 * No browser, no Playwright — just file reading and regex/string parsing.
 */

const fs   = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Read a file to a string, normalising CRLF to LF.
 * @param {string} filePath
 * @returns {string}
 */
function readCSS(filePath) {
  return fs.readFileSync(filePath, 'utf8').replace(/\r\n/g, '\n');
}

/**
 * Collect all .css file paths in a directory (non-recursive by default).
 * @param {string} cssDir
 * @returns {string[]}
 */
function collectCSSFiles(cssDir) {
  return fs
    .readdirSync(cssDir)
    .filter((f) => f.endsWith('.css'))
    .map((f) => path.join(cssDir, f));
}

/**
 * Strip block and line comments from a CSS string.
 * @param {string} css
 * @returns {string}
 */
function stripComments(css) {
  return css.replace(/\/\*[\s\S]*?\*\//g, '');
}

/**
 * Parse a flat `property: value` declaration block into a map.
 * @param {string} declarationBlock  e.g. "color: red; font-size: 1rem;"
 * @returns {Record<string, string>}
 */
function parseDeclarations(declarationBlock) {
  const result = {};
  const lines  = declarationBlock.split(';');
  for (const line of lines) {
    const colonIdx = line.indexOf(':');
    if (colonIdx === -1) continue;
    const prop  = line.slice(0, colonIdx).trim();
    const value = line.slice(colonIdx + 1).trim();
    if (prop) result[prop] = value;
  }
  return result;
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * parseCSSClass
 * Reads a CSS file, finds the first rule block whose selector matches `selector`,
 * and returns a `{ property: value }` map of its declarations.
 *
 * The selector match is an exact string equality after normalising whitespace.
 * For class selectors pass e.g. ".shell-card".
 *
 * @param {string} filePath   Absolute (or CWD-relative) path to a CSS file.
 * @param {string} selector   Selector to locate, e.g. ".shell-card" or ".badge".
 * @returns {Record<string, string>}  Empty object if selector not found.
 */
function parseCSSClass(filePath, selector) {
  const raw = stripComments(readCSS(filePath));

  // We scan the file character-by-character to handle nested braces (media queries)
  // and to match the selector exactly at rule level.
  const normSelector = selector.trim();
  let i = 0;
  const len = raw.length;

  while (i < len) {
    // Advance until we find something that looks like a block opener.
    const braceIdx = raw.indexOf('{', i);
    if (braceIdx === -1) break;

    // The "selector text" is everything between the last '}' (or start) and this '{'.
    // We need to find the start of this rule — walk backwards past whitespace.
    const candidateSelectorRaw = raw.slice(i, braceIdx);

    // Split by comma to handle grouped selectors, trim each part.
    const candidates = candidateSelectorRaw
      .split(',')
      .map((s) => s.replace(/\s+/g, ' ').trim());

    // Find the matching closing brace, respecting nesting.
    let depth = 1;
    let j = braceIdx + 1;
    while (j < len && depth > 0) {
      if (raw[j] === '{') depth++;
      else if (raw[j] === '}') depth--;
      j++;
    }
    const blockContent = raw.slice(braceIdx + 1, j - 1);

    if (candidates.some((c) => c === normSelector)) {
      // Only parse if this is a simple (non-nested) rule — no inner braces.
      if (!blockContent.includes('{')) {
        return parseDeclarations(blockContent);
      }
    }

    i = j;
  }

  return {};
}

/**
 * parseRootTokens
 * Reads a CSS file, finds the `:root` block, and returns a `{ tokenName: value }` map.
 * Token names include the leading `--`, e.g. `"--color-accent"`.
 *
 * @param {string} filePath
 * @returns {Record<string, string>}
 */
function parseRootTokens(filePath) {
  return parseCSSClass(filePath, ':root');
}

/**
 * getAnimatedSelectors
 * Scans all .css files in `cssDir` and returns an array of selectors that have
 * `animation` or `transition` declarations in their rule bodies.
 *
 * Selectors inside @keyframes blocks are excluded.
 *
 * @param {string} cssDir  Directory path (absolute or relative).
 * @returns {string[]}
 */
function getAnimatedSelectors(cssDir) {
  const files = collectCSSFiles(cssDir);
  const selectors = new Set();

  for (const file of files) {
    const raw = stripComments(readCSS(file));
    // Walk each top-level rule block.
    let i = 0;
    const len = raw.length;

    while (i < len) {
      const braceIdx = raw.indexOf('{', i);
      if (braceIdx === -1) break;

      const candidateSelectorRaw = raw.slice(i, braceIdx).trim();

      // Skip @keyframes and @media / @supports at-rules (which contain nested rules).
      const isAtRule = candidateSelectorRaw.startsWith('@');

      let depth = 1;
      let j = braceIdx + 1;
      while (j < len && depth > 0) {
        if (raw[j] === '{') depth++;
        else if (raw[j] === '}') depth--;
        j++;
      }
      const blockContent = raw.slice(braceIdx + 1, j - 1);

      if (!isAtRule) {
        // Check for animation or transition declarations.
        const hasAnimation =
          /\banimation\s*:/.test(blockContent) ||
          /\banimation-name\s*:/.test(blockContent);
        const hasTransition = /\btransition\s*:/.test(blockContent);

        if (hasAnimation || hasTransition) {
          // Split comma-grouped selectors and record each.
          candidateSelectorRaw
            .split(',')
            .map((s) => s.replace(/\s+/g, ' ').trim())
            .filter(Boolean)
            .forEach((s) => selectors.add(s));
        }
      }

      i = j;
    }
  }

  return Array.from(selectors);
}

/**
 * getReducedMotionOverrides
 * Scans all .css files in `cssDir` and returns a Set of selectors that appear
 * inside `@media (prefers-reduced-motion: reduce)` blocks.
 *
 * @param {string} cssDir
 * @returns {Set<string>}
 */
function getReducedMotionOverrides(cssDir) {
  const files = collectCSSFiles(cssDir);
  const overrides = new Set();

  // Regex to find the prefers-reduced-motion media query block.
  // We do a character scan because the block may span many lines.
  const mediaQueryPattern = /@media\s*\(\s*prefers-reduced-motion\s*:\s*reduce\s*\)/i;

  for (const file of files) {
    const raw = stripComments(readCSS(file));

    let searchFrom = 0;
    let match;
    // Find each occurrence of the media query.
    const re = new RegExp(mediaQueryPattern.source, 'gi');

    while ((match = re.exec(raw)) !== null) {
      const braceStart = raw.indexOf('{', match.index);
      if (braceStart === -1) continue;

      // Extract the contents of the @media block.
      let depth = 1;
      let k = braceStart + 1;
      while (k < raw.length && depth > 0) {
        if (raw[k] === '{') depth++;
        else if (raw[k] === '}') depth--;
        k++;
      }
      const mediaContent = raw.slice(braceStart + 1, k - 1);

      // Now parse rules inside the media block.
      let mi = 0;
      while (mi < mediaContent.length) {
        const innerBrace = mediaContent.indexOf('{', mi);
        if (innerBrace === -1) break;
        const innerSelector = mediaContent.slice(mi, innerBrace).trim();
        // Find the matching closing brace for this inner rule.
        let depth2 = 1;
        let mj = innerBrace + 1;
        while (mj < mediaContent.length && depth2 > 0) {
          if (mediaContent[mj] === '{') depth2++;
          else if (mediaContent[mj] === '}') depth2--;
          mj++;
        }
        innerSelector
          .split(',')
          .map((s) => s.replace(/\s+/g, ' ').trim())
          .filter(Boolean)
          .forEach((s) => overrides.add(s));

        mi = mj;
      }
    }
  }

  return overrides;
}

/**
 * getAllCSSPropertyValues
 * Returns all values of a given CSS property found in rule bodies across all CSS files
 * in `cssDir`. Excludes declarations inside `:root {}`.
 *
 * @param {string} cssDir
 * @param {string} property  e.g. "background", "border-radius", "font-family"
 * @returns {string[]}  All distinct values found (may contain duplicates if desired
 *                      — deduplicate externally).
 */
function getAllCSSPropertyValues(cssDir, property) {
  const files = collectCSSFiles(cssDir);
  const values = [];

  // Build a regex that matches "property : <value>" at declaration level.
  // We look for the property name followed by colon and value up to `;` or end of block.
  const propRe = new RegExp(
    `(?:^|[;{\\n])\\s*${escapeRegExp(property)}\\s*:\\s*([^;}]+)`,
    'gi'
  );

  for (const file of files) {
    const raw = stripComments(readCSS(file));

    // Remove :root block first so we don't pick up token declarations.
    const withoutRoot = removeRootBlock(raw);

    let m;
    propRe.lastIndex = 0;
    while ((m = propRe.exec(withoutRoot)) !== null) {
      const value = m[1].trim();
      if (value) values.push(value);
    }
  }

  return values;
}

/**
 * parseMediaQuery
 * Returns a `{ property: value }` map for a given selector within a specific
 * media query string in a CSS file.
 *
 * @param {string} filePath
 * @param {string} selector      e.g. ".hero-grid"
 * @param {string} mediaQuery    e.g. "(min-width: 1024px)"
 * @returns {Record<string, string>}
 */
function parseMediaQuery(filePath, selector, mediaQuery) {
  const raw = stripComments(readCSS(filePath));
  const normSelector = selector.trim();

  // Locate @media blocks that match the given query string (case-insensitive,
  // normalise whitespace for matching).
  const normQuery = mediaQuery.replace(/\s+/g, ' ').trim();
  const re = /@media\s+([^{]+)\{/gi;
  let match;

  while ((match = re.exec(raw)) !== null) {
    const queryText = match[1].replace(/\s+/g, ' ').trim();
    if (queryText !== normQuery) continue;

    // Extract the @media block body.
    const braceStart = match.index + match[0].length - 1;
    let depth = 1;
    let k = braceStart + 1;
    while (k < raw.length && depth > 0) {
      if (raw[k] === '{') depth++;
      else if (raw[k] === '}') depth--;
      k++;
    }
    const mediaBody = raw.slice(braceStart + 1, k - 1);

    // Now find the selector inside the media body.
    let mi = 0;
    while (mi < mediaBody.length) {
      const innerBrace = mediaBody.indexOf('{', mi);
      if (innerBrace === -1) break;
      const innerSelectorRaw = mediaBody.slice(mi, innerBrace);
      const innerSelectors = innerSelectorRaw
        .split(',')
        .map((s) => s.replace(/\s+/g, ' ').trim());

      let depth2 = 1;
      let mj = innerBrace + 1;
      while (mj < mediaBody.length && depth2 > 0) {
        if (mediaBody[mj] === '{') depth2++;
        else if (mediaBody[mj] === '}') depth2--;
        mj++;
      }
      const blockContent = mediaBody.slice(innerBrace + 1, mj - 1);

      if (innerSelectors.some((s) => s === normSelector)) {
        return parseDeclarations(blockContent);
      }

      mi = mj;
    }
  }

  return {};
}

// ---------------------------------------------------------------------------
// Private helpers
// ---------------------------------------------------------------------------

/**
 * Escape a string for use inside a RegExp.
 * @param {string} str
 * @returns {string}
 */
function escapeRegExp(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Remove the `:root { ... }` block from a CSS string.
 * @param {string} css
 * @returns {string}
 */
function removeRootBlock(css) {
  // Find `:root` and extract its block.
  const idx = css.search(/:root\s*\{/);
  if (idx === -1) return css;

  const braceStart = css.indexOf('{', idx);
  let depth = 1;
  let k = braceStart + 1;
  while (k < css.length && depth > 0) {
    if (css[k] === '{') depth++;
    else if (css[k] === '}') depth--;
    k++;
  }

  return css.slice(0, idx) + css.slice(k);
}

// ---------------------------------------------------------------------------
// Exports
// ---------------------------------------------------------------------------

module.exports = {
  parseCSSClass,
  parseRootTokens,
  getAnimatedSelectors,
  getReducedMotionOverrides,
  getAllCSSPropertyValues,
  parseMediaQuery,
};
