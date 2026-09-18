#!/usr/bin/env node
// Deterministic Markdown checks: relative link targets, heading anchors and
// stale "Last checked" dates. No dependencies. Its output is evidence for what
// it checked; it grants no authority and replaces no review.
//
// Usage: node tools/check-docs.mjs [--max-age <days>] [path ...]
//   path       Files or directories to scan (default: current directory).
//   --max-age  Warn when a "Last checked: YYYY-MM-DD" date is older (default 90).
// Exit code: 1 when a link or anchor does not resolve, otherwise 0.
// Warnings never change the exit code.

import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, extname, join, relative, resolve, sep } from 'node:path';

const SKIP_DIRS = new Set(['.git', 'node_modules', '.venv', '.harness']);
const LINK = /!?\[((?:[^\[\]]|\[[^\]]*\])*)\]\(\s*(<[^>]*>|[^()\s]+(?:\([^()]*\)[^()\s]*)*)(?:\s+(?:"[^"]*"|'[^']*'))?\s*\)/g;
const REFERENCE = /^ {0,3}\[[^\]]+\]:\s*(<[^>]*>|\S+)/gm;
const HEADING = /^ {0,3}#{1,6}[ \t]+(.*?)[ \t]*#*[ \t]*$/;
const EXPLICIT_ID = /<[a-zA-Z][^>]*\s(?:id|name)\s*=\s*["']([^"']+)["']/g;
const LAST_CHECKED = /Last checked:\s*(\d{4})-(\d{2})-(\d{2})/g;

function parseArgs(argv) {
  const options = { maxAge: 90, paths: [] };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--max-age') {
      options.maxAge = Number(argv[i + 1]);
      i += 1;
      if (!Number.isFinite(options.maxAge)) {
        throw new Error('--max-age needs a number of days');
      }
    } else {
      options.paths.push(argv[i]);
    }
  }
  if (options.paths.length === 0) options.paths.push('.');
  return options;
}

function collectMarkdown(path, found) {
  const stats = statSync(path);
  if (stats.isFile()) {
    if (extname(path).toLowerCase() === '.md') found.add(resolve(path));
    return;
  }
  for (const entry of readdirSync(path, { withFileTypes: true })) {
    if (entry.isDirectory() && SKIP_DIRS.has(entry.name)) continue;
    collectMarkdown(join(path, entry.name), found);
  }
}

// Blank out fenced blocks and inline code so that examples are not checked,
// keeping every newline and offset so reported line numbers stay accurate.
function blankCode(text) {
  const lines = text.split('\n');
  let fence = null;
  for (let i = 0; i < lines.length; i += 1) {
    const marker = lines[i].match(/^ {0,3}(`{3,}|~{3,})/);
    if (fence) {
      const closes = marker && marker[1][0] === fence[0] && marker[1].length >= fence.length;
      lines[i] = ' '.repeat(lines[i].length);
      if (closes) fence = null;
    } else if (marker) {
      fence = marker[1];
      lines[i] = ' '.repeat(lines[i].length);
    }
  }
  return lines
    .join('\n')
    .replace(/(`+)(?!`)[^\n]*?[^`\n]\1(?!`)/g, (span) => ' '.repeat(span.length));
}

// GitHub heading anchors: lowercase, drop punctuation, spaces to hyphens and a
// numeric suffix for repeated headings.
function slugify(heading, seen) {
  const plain = heading
    .replace(/!?\[((?:[^\[\]]|\[[^\]]*\])*)\]\([^)]*\)/g, '$1')
    .replace(/<[^>]+>/g, '')
    .replace(/[`*]/g, '');
  const base = plain
    .trim()
    .toLowerCase()
    .replace(/[^\p{L}\p{M}\p{N}\p{Pc} -]/gu, '')
    .replace(/ /g, '-');
  const count = seen.get(base) ?? 0;
  seen.set(base, count + 1);
  return count === 0 ? base : `${base}-${count}`;
}

function anchorsOf(file, cache) {
  if (cache.has(file)) return cache.get(file);
  const raw = readFileSync(file, 'utf8').replace(/\r\n/g, '\n');
  const anchors = new Set();
  const seen = new Map();
  let fence = null;
  for (const line of raw.split('\n')) {
    const marker = line.match(/^ {0,3}(`{3,}|~{3,})/);
    if (fence) {
      if (marker && marker[1][0] === fence[0] && marker[1].length >= fence.length) fence = null;
      continue;
    }
    if (marker) {
      fence = marker[1];
      continue;
    }
    const heading = line.match(HEADING);
    if (heading) anchors.add(slugify(heading[1], seen));
  }
  for (const match of blankCode(raw).matchAll(EXPLICIT_ID)) anchors.add(match[1]);
  cache.set(file, anchors);
  return anchors;
}

function lineAt(text, index) {
  let line = 1;
  for (let i = 0; i < index; i += 1) if (text[i] === '\n') line += 1;
  return line;
}

function decode(value) {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

function checkFile(file, cache, options, report) {
  const text = blankCode(readFileSync(file, 'utf8').replace(/\r\n/g, '\n'));
  const targets = [];
  for (const match of text.matchAll(LINK)) targets.push([match[2], match.index]);
  for (const match of text.matchAll(REFERENCE)) targets.push([match[1], match.index]);

  for (const [rawTarget, index] of targets) {
    const target = rawTarget.replace(/^<|>$/g, '');
    if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(target) || target.startsWith('//')) continue;
    const hash = target.indexOf('#');
    const pathPart = decode(hash === -1 ? target : target.slice(0, hash));
    const anchor = hash === -1 ? '' : decode(target.slice(hash + 1));
    const destination = pathPart === '' ? file : resolve(dirname(file), pathPart);

    if (!existsSync(destination)) {
      report.errors.push([file, lineAt(text, index), `missing target: ${target}`]);
      continue;
    }
    if (anchor === '' || extname(destination).toLowerCase() !== '.md') continue;
    if (!statSync(destination).isFile()) continue;
    if (!anchorsOf(destination, cache).has(anchor.toLowerCase())) {
      report.errors.push([file, lineAt(text, index), `missing anchor: ${target}`]);
    }
  }

  for (const match of text.matchAll(LAST_CHECKED)) {
    const checked = Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
    const age = Math.floor((options.now - checked) / 86400000);
    if (age > options.maxAge) {
      report.warnings.push([
        file,
        lineAt(text, match.index),
        `last checked ${age} days ago (limit ${options.maxAge}): recheck the dated facts here`,
      ]);
    }
  }
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  options.now = Date.now();
  const files = new Set();
  for (const path of options.paths) {
    if (!existsSync(path)) throw new Error(`path not found: ${path}`);
    collectMarkdown(path, files);
  }

  const report = { errors: [], warnings: [] };
  const cache = new Map();
  for (const file of [...files].sort()) checkFile(file, cache, options, report);

  const show = ([file, line, message]) =>
    `${relative(process.cwd(), file).split(sep).join('/')}:${line}: ${message}`;
  for (const entry of report.warnings) console.log(`warning ${show(entry)}`);
  for (const entry of report.errors) console.log(`error   ${show(entry)}`);
  console.log(
    `checked ${files.size} Markdown files: ${report.errors.length} errors, ${report.warnings.length} warnings`,
  );
  process.exit(report.errors.length > 0 ? 1 : 0);
}

try {
  main();
} catch (error) {
  console.error(`check-docs: ${error.message}`);
  process.exit(2);
}
