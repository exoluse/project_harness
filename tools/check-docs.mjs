#!/usr/bin/env node
// Deterministic Markdown checks: relative link targets, heading anchors, stale
// "Last checked" dates and ID-named documents (`<ID>.md`, `<ID>-<slug>.md`).
// No dependencies. Its output is evidence for what it checked; it grants no
// authority and replaces no review.
//
// Usage: node tools/check-docs.mjs [--max-age <days>] [path ...]
//   path       Files or directories to scan (default: current directory).
//              Inside a Git work tree a directory yields the Markdown files Git
//              tracks or would track, so .gitignore applies; elsewhere it is
//              walked. A file given by name is always checked.
//   --max-age  Warn when a "Last checked: YYYY-MM-DD" date is older (default 90).
// Exit code: 1 when a link or anchor does not resolve, a link's path differs in
// letter case from the file on disk, or two scanned files own the same ID,
// otherwise 0. Warnings never change the exit code.
//
// ID checks read the ID from the filename, so files with other names, such as
// harness guidance and required-name files, are not examined. They know nothing
// of a project's format table, allocation record or retired IDs.

import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { basename, dirname, extname, isAbsolute, join, relative, resolve, sep } from 'node:path';

const SKIP_DIRS = new Set(['.git', 'node_modules', '.venv', '.harness']);
const LINK = /!?\[((?:[^\[\]]|\[[^\]]*\])*)\]\(\s*(<[^>]*>|[^()\s]+(?:\([^()]*\)[^()\s]*)*)(?:\s+(?:"[^"]*"|'[^']*'))?\s*\)/g;
// Link reference definitions; a footnote definition (`[^1]: text`) is not one.
const REFERENCE = /^ {0,3}\[(?!\^)[^\]]+\]:\s*(<[^>]*>|\S+)/gm;
const HEADING = /^ {0,3}#{1,6}[ \t]+(.*?)[ \t]*#*[ \t]*$/;
const EXPLICIT_ID = /<[a-zA-Z][^>]*\s(?:id|name)\s*=\s*["']([^"']+)["']/g;
const LAST_CHECKED = /Last checked:\s*(\d{4})-(\d{2})-(\d{2})/g;
// Uppercase/digit segments ending in a serial: REQ-001, TASK-API-001, OD-012-01.
const ID = '[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\\d+';
const ID_FILENAME = new RegExp(`^(${ID})(?:-(.+))?\\.md$`);
const ID_ONLY = new RegExp(`^${ID}$`);
const SLUG = /^[a-z]+-[a-z]+$/;

function parseArgs(argv) {
  const options = { maxAge: 90, paths: [], scannedDirectory: false };
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

function isMarkdown(path) {
  return extname(path).toLowerCase() === '.md';
}

function ignoredByGit(directory) {
  const path = resolve(directory);
  try {
    execFileSync('git', ['-C', dirname(path), 'check-ignore', '-q', basename(path)], {
      stdio: 'ignore',
    });
    return true;
  } catch {
    return false;
  }
}

// Markdown files under a directory that Git tracks or would track, honoring
// .gitignore. Returns null outside a work tree, without Git, or for an ignored
// directory named explicitly; the walk applies then.
function gitMarkdown(directory) {
  let output;
  try {
    output = execFileSync(
      'git',
      ['-C', directory, 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
      { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], maxBuffer: 256 * 1024 * 1024 },
    );
  } catch {
    return null;
  }
  const files = output
    .split('\0')
    .filter((path) => path !== '' && isMarkdown(path))
    .filter((path) => !path.split('/').some((segment) => SKIP_DIRS.has(segment)))
    .map((path) => resolve(directory, path))
    .filter((path) => existsSync(path));
  if (files.length === 0 && ignoredByGit(directory)) return null;
  return files;
}

function walkMarkdown(path, found) {
  if (statSync(path).isFile()) {
    if (isMarkdown(path)) found.add(resolve(path));
    return;
  }
  for (const entry of readdirSync(path, { withFileTypes: true })) {
    if (entry.isDirectory() && SKIP_DIRS.has(entry.name)) continue;
    walkMarkdown(join(path, entry.name), found);
  }
}

function collectMarkdown(path, found) {
  if (statSync(path).isDirectory()) {
    const listed = gitMarkdown(path);
    if (listed) {
      for (const file of listed) found.add(file);
      return;
    }
  }
  walkMarkdown(path, found);
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

// Heading text and 1-based line of every heading outside fenced blocks.
function headingsOf(raw) {
  const headings = [];
  let fence = null;
  raw.split('\n').forEach((line, index) => {
    const marker = line.match(/^ {0,3}(`{3,}|~{3,})/);
    if (fence) {
      if (marker && marker[1][0] === fence[0] && marker[1].length >= fence.length) fence = null;
      return;
    }
    if (marker) {
      fence = marker[1];
      return;
    }
    const heading = line.match(HEADING);
    if (heading) headings.push([heading[1], index + 1]);
  });
  return headings;
}

// Heading slugs are lowercase and match a fragment of any case, as before.
// Explicit HTML ids keep their case, which an HTML fragment must match exactly.
function anchorsOf(file, cache) {
  if (cache.has(file)) return cache.get(file);
  const raw = readFileSync(file, 'utf8').replace(/\r\n/g, '\n');
  const anchors = { headings: new Set(), explicit: new Set() };
  const seen = new Map();
  for (const [heading] of headingsOf(raw)) anchors.headings.add(slugify(heading, seen));
  for (const match of blankCode(raw).matchAll(EXPLICIT_ID)) anchors.explicit.add(match[1]);
  cache.set(file, anchors);
  return anchors;
}

function hasAnchor(anchors, anchor) {
  return anchors.explicit.has(anchor) || anchors.headings.has(anchor.toLowerCase());
}

const entriesCache = new Map();

function entriesOf(directory) {
  if (!entriesCache.has(directory)) {
    let names = [];
    try {
      names = readdirSync(directory);
    } catch {
      // An unreadable directory leaves nothing to compare.
    }
    entriesCache.set(directory, names);
  }
  return entriesCache.get(directory);
}

// A case-insensitive filesystem resolves a link whose letter case differs from
// the file name, and the link then breaks on GitHub or Linux. Compare each
// segment the link itself names with the names on disk; returns the first
// differing segment and its actual name, or null.
function caseMismatch(fromDirectory, pathPart) {
  if (isAbsolute(pathPart)) return null;
  let current = fromDirectory;
  for (const segment of pathPart.split(/[\\/]/)) {
    if (segment === '' || segment === '.') continue;
    if (segment === '..') {
      current = dirname(current);
      continue;
    }
    const names = entriesOf(current);
    if (!names.includes(segment)) {
      const actual = names.find((name) => name.toLowerCase() === segment.toLowerCase());
      return actual === undefined ? null : [segment, actual];
    }
    current = join(current, segment);
  }
  return null;
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

// Paths compare case-insensitively where the filesystem does.
function pathKey(path) {
  return process.platform === 'win32' ? path.toLowerCase() : path;
}

// Returns what the ID checks need: the file's ID, the Markdown files it links
// to and its ID-only headings, which mark item definitions.
function checkFile(file, cache, options, report) {
  const raw = readFileSync(file, 'utf8').replace(/\r\n/g, '\n');
  const text = blankCode(raw);
  const linked = new Set();
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
    const mismatch = pathPart === '' ? null : caseMismatch(dirname(file), pathPart);
    if (mismatch) {
      report.errors.push([
        file,
        lineAt(text, index),
        `letter case differs from disk: ${target} ("${mismatch[0]}" is "${mismatch[1]}" on disk)`,
      ]);
    }
    if (extname(destination).toLowerCase() !== '.md') continue;
    if (!statSync(destination).isFile()) continue;
    linked.add(pathKey(destination));
    if (anchor === '') continue;
    if (!hasAnchor(anchorsOf(destination, cache), anchor)) {
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

  const definitions = [];
  for (const [heading, line] of headingsOf(raw)) {
    const plain = heading.replace(/[`*]/g, '').trim();
    if (ID_ONLY.test(plain)) definitions.push([plain, line]);
  }

  const named = basename(file).match(ID_FILENAME);
  if (!named) return { id: null, linked, definitions };
  const [, id, slug] = named;
  if (slug !== undefined && !SLUG.test(slug)) {
    report.warnings.push([
      file,
      1,
      `filename description "${slug}" is not two lowercase words joined by a hyphen`,
    ]);
  }
  if (!new RegExp(`(?<![A-Za-z0-9-])${id}(?!-?[A-Za-z0-9])`).test(raw)) {
    report.warnings.push([file, 1, `ID ${id} from the filename does not appear in the body`]);
  }
  return { id, linked, definitions };
}

function showPath(file) {
  return relative(process.cwd(), file).split(sep).join('/');
}

// One owning file and one definition per ID, and an incoming link for every
// ID-named file.
function checkIds(scanned, options, report) {
  const owners = new Map();
  const headings = new Map();
  for (const [file, { id, definitions }] of scanned) {
    if (id) owners.set(id, [...(owners.get(id) ?? []), file]);
    for (const [defined, line] of definitions) {
      if (defined === id) continue;
      headings.set(defined, [...(headings.get(defined) ?? []), [file, line]]);
    }
  }
  for (const [id, files] of owners) {
    if (files.length < 2) continue;
    for (const file of files) {
      const others = files.filter((other) => other !== file).map(showPath).join(', ');
      report.errors.push([file, 1, `ID ${id} has another owning file: ${others}`]);
    }
  }
  for (const [id, sites] of headings) {
    const all = [
      ...(owners.get(id) ?? []).map(showPath),
      ...sites.map(([file, line]) => `${showPath(file)}:${line}`),
    ];
    if (all.length < 2) continue;
    for (const [file, line] of sites) {
      const others = all.filter((site) => site !== `${showPath(file)}:${line}`).join(', ');
      report.warnings.push([file, line, `ID-only heading ${id} is also defined at ${others}`]);
    }
  }

  // Incoming links are only known when a directory was scanned. The unlinked
  // document that links to the most items is taken as the project overview.
  if (!options.scannedDirectory) return;
  const idFiles = new Set();
  const incoming = new Set();
  for (const [file, { id, linked }] of scanned) {
    if (id) idFiles.add(pathKey(file));
    for (const target of linked) if (target !== pathKey(file)) incoming.add(target);
  }
  // A lone ID-named file has no item that could link it: it is the overview,
  // such as a compact work document serving that role.
  if (idFiles.size === 1) return;
  const unlinked = [];
  for (const [file, { id, linked }] of scanned) {
    if (!id || incoming.has(pathKey(file))) continue;
    const items = [...linked].filter((target) => idFiles.has(target) && target !== pathKey(file));
    unlinked.push([file, items.length]);
  }
  const most = Math.max(0, ...unlinked.map(([, count]) => count));
  const overviews = unlinked.filter(([, count]) => most > 0 && count === most);
  for (const [file] of unlinked) {
    if (overviews.length === 1 && overviews[0][0] === file) continue;
    report.warnings.push([
      file,
      1,
      'no scanned document links here: link it from its overview or owning plan',
    ]);
  }
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  options.now = Date.now();
  const files = new Set();
  for (const path of options.paths) {
    if (!existsSync(path)) throw new Error(`path not found: ${path}`);
    if (statSync(path).isDirectory()) options.scannedDirectory = true;
    collectMarkdown(path, files);
  }

  const report = { errors: [], warnings: [] };
  const cache = new Map();
  const scanned = new Map();
  for (const file of [...files].sort()) scanned.set(file, checkFile(file, cache, options, report));
  checkIds(scanned, options, report);

  const show = ([file, line, message]) => `${showPath(file)}:${line}: ${message}`;
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
