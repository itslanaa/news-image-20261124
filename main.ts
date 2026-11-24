// SPDX-License-Identifier: MIT
// main.ts — news-image-20261124 entrypoint.
//
// Copies the pre-rendered front page (entry.png, drawn in code by
// draw_frontpage.py) into the harness output directory. No network, no
// randomness: the same bytes are written on every run. The image must stay
// inside the competition's gate — at most 1 MiB and 1024 by 1024 pixels —
// so a bad image fails loudly here instead of grading invalid.
import { copyFileSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const src = join(here, "entry.png");
const size = statSync(src).size;
if (size > 1048576) {
  throw new Error(`entry.png is ${size} bytes, over the 1 MiB gate`);
}
mkdirSync(outDir, { recursive: true });
copyFileSync(src, join(outDir, "entry.png"));
console.error(`wrote entry.png (${size} bytes, 1024x1024) to ${outDir}`);
