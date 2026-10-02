// Regression tests for check-docs.mjs. Run: node --test tools/check-docs.test.mjs
// Fixtures are written to a temporary directory, never to this repository,
// because their deliberately broken links would fail the repository's own check.

import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { after, test } from 'node:test';
import { fileURLToPath } from 'node:url';

const CHECKER = join(dirname(fileURLToPath(import.meta.url)), 'check-docs.mjs');
const ROOT = mkdtempSync(join(tmpdir(), 'check-docs-test-'));
// Keep Git from finding a repository above the fixtures.
const ENV = { ...process.env, GIT_CEILING_DIRECTORIES: dirname(ROOT) };

after(() => rmSync(ROOT, { recursive: true, force: true }));

let fixtures = 0;

// Writes the given files into a fresh directory and returns its path.
function fixture(files) {
  fixtures += 1;
  const directory = join(ROOT, `case-${fixtures}`);
  mkdirSync(directory, { recursive: true });
  for (const [path, content] of Object.entries(files)) {
    const full = join(directory, path);
    mkdirSync(dirname(full), { recursive: true });
    writeFileSync(full, content);
  }
  return directory;
}

function check(cwd, ...args) {
  const result = spawnSync(process.execPath, [CHECKER, ...args], {
    cwd,
    env: ENV,
    encoding: 'utf8',
  });
  return { status: result.status, out: `${result.stdout}${result.stderr}` };
}

function gitAvailable() {
  try {
    execFileSync('git', ['--version'], { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

test('a clean document set passes', () => {
  const directory = fixture({
    'index.md': '# Index\n\nSee [the guide](guide.md#getting-started).\n',
    'guide.md': '# Guide\n\n## Getting started\n',
  });
  const { status, out } = check(directory, '.');
  assert.equal(status, 0);
  assert.match(out, /checked 2 Markdown files: 0 errors, 0 warnings/);
});

test('a missing link target fails', () => {
  const directory = fixture({ 'index.md': '# Index\n\n[gone](missing.md)\n' });
  const { status, out } = check(directory, '.');
  assert.equal(status, 1);
  assert.match(out, /index\.md:3: missing target: missing\.md/);
});

test('heading anchors match a fragment of any case', () => {
  const directory = fixture({
    'index.md': '# Getting Started\n\n[ok](#Getting-Started) [bad](#no-such-heading)\n',
  });
  const { status, out } = check(directory, '.');
  assert.equal(status, 1);
  assert.doesNotMatch(out, /#Getting-Started/);
  assert.match(out, /missing anchor: #no-such-heading/);
});

test('explicit HTML ids keep their case', () => {
  const directory = fixture({
    'index.md': '# Items\n\n<a id="REQ-001"></a>Sign-in\n\n[ok](#REQ-001) [bad](#req-001)\n',
  });
  const { status, out } = check(directory, '.');
  assert.equal(status, 1);
  assert.doesNotMatch(out, /#REQ-001/);
  assert.match(out, /missing anchor: #req-001/);
});

test('footnote definitions are not link references', () => {
  const directory = fixture({
    'index.md': '# Notes\n\nText.[^1] See [ref][r].\n\n[^1]: Customer email.\n[r]: missing.md\n',
  });
  const { status, out } = check(directory, '.');
  assert.equal(status, 1);
  assert.doesNotMatch(out, /Customer/);
  assert.match(out, /missing target: missing\.md/);
});

test('links inside code are not checked', () => {
  const directory = fixture({
    'index.md': '# Code\n\n`[x](missing.md)`\n\n```text\n[y](missing.md)\n```\n',
  });
  const { status } = check(directory, '.');
  assert.equal(status, 0);
});

test('a link whose letter case differs from the file fails', () => {
  const directory = fixture({
    'index.md': '# Index\n\n[guide](Docs/Guide.md)\n',
    'docs/guide.md': '# Guide\n',
  });
  const caseInsensitive = existsSync(join(directory, 'INDEX.MD'));
  const { status, out } = check(directory, '.');
  assert.equal(status, 1);
  // A case-insensitive filesystem finds the file; a case-sensitive one does not.
  assert.match(
    out,
    caseInsensitive
      ? /letter case differs from disk: Docs\/Guide\.md \("Docs" is "docs" on disk\)/
      : /missing target: Docs\/Guide\.md/,
  );
});

test('a stale Last checked date warns without failing', () => {
  const directory = fixture({ 'tool.md': '# Tool\n\nLast checked: 2000-01-01 against the docs.\n' });
  const { status, out } = check(directory, '--max-age', '30', '.');
  assert.equal(status, 0);
  assert.match(out, /tool\.md:3: last checked \d+ days ago \(limit 30\)/);
});

test('ID-named files: duplicate owners fail; slug and body problems warn', () => {
  const directory = fixture({
    'overview/DOC-001.md':
      '# DOC-001\n\n[a](../a/REQ-001.md) [b](../b/REQ-001-login-form.md) ' +
      '[c](../REQ-002-login.md) [d](../REQ-003.md)\n',
    'a/REQ-001.md': '# REQ-001\n',
    'b/REQ-001-login-form.md': '# REQ-001\n',
    'REQ-002-login.md': '# REQ-002\n',
    'REQ-003.md': '# Untitled requirement\n',
  });
  const { status, out } = check(directory, '.');
  assert.equal(status, 1);
  assert.match(out, /error {3}a\/REQ-001\.md:1: ID REQ-001 has another owning file: b\/REQ-001-login-form\.md/);
  assert.match(out, /REQ-002-login\.md:1: filename description "login" is not two lowercase words/);
  assert.match(out, /REQ-003\.md:1: ID REQ-003 from the filename does not appear in the body/);
  assert.doesNotMatch(out, /no scanned document links here/);
});

test('an unlinked ID-named file warns, except the overview', () => {
  const directory = fixture({
    'overview/DOC-001.md': '# DOC-001\n\n[one](../tasks/TASK-001.md) [two](../tasks/TASK-002.md)\n',
    'tasks/TASK-001.md': '# TASK-001\n',
    'tasks/TASK-002.md': '# TASK-002\n',
    'tasks/TASK-003.md': '# TASK-003\n',
  });
  const { status, out } = check(directory, '.');
  assert.equal(status, 0);
  assert.match(out, /tasks\/TASK-003\.md:1: no scanned document links here/);
  assert.doesNotMatch(out, /DOC-001\.md:1: no scanned/);
});

test('a lone ID-named file is taken as the overview', () => {
  const directory = fixture({ 'tasks/TASK-001.md': '# TASK-001\n\nCompact work document.\n' });
  const { status, out } = check(directory, '.');
  assert.equal(status, 0);
  assert.match(out, /0 errors, 0 warnings/);
});

test('inside Git, ignored directories are skipped unless named', { skip: !gitAvailable() }, () => {
  const directory = fixture({
    '.gitignore': 'dist/\nsite/build/\n',
    'docs/ok.md': '# OK\n',
    'dist/bad.md': '# Bad\n\n[x](missing.md)\n',
    'site/build/bad.md': '# Bad\n\n[x](missing.md)\n',
  });
  execFileSync('git', ['init', '-q', directory], { env: ENV, stdio: 'ignore' });

  const root = check(directory, '.');
  assert.equal(root.status, 0);
  assert.match(root.out, /checked 1 Markdown files/);

  const site = check(directory, 'site');
  assert.equal(site.status, 0);
  assert.match(site.out, /checked 0 Markdown files/);

  const named = check(directory, 'dist');
  assert.equal(named.status, 1);
  assert.match(named.out, /dist\/bad\.md:3: missing target: missing\.md/);
});

test('outside Git, a directory is walked', () => {
  const directory = fixture({ 'dist/bad.md': '# Bad\n\n[x](missing.md)\n', '.gitignore': 'dist/\n' });
  const { status, out } = check(directory, '.');
  assert.equal(status, 1);
  assert.match(out, /missing target: missing\.md/);
});

test('a path that does not exist exits with 2', () => {
  const { status, out } = check(ROOT, 'no-such-path');
  assert.equal(status, 2);
  assert.match(out, /check-docs: path not found/);
});
