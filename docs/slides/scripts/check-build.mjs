import { existsSync, readFileSync } from 'node:fs'
import { join, normalize } from 'node:path'

const base = process.env.PAGES_BASE || '/'
const indexPath = 'dist/index.html'

if (!existsSync(indexPath)) {
  console.error(`Missing build entry: ${indexPath}`)
  process.exit(1)
}

const html = readFileSync(indexPath, 'utf8')
if (base !== '/' && !html.includes(base)) {
  console.error(`Build output does not contain the expected base path: ${base}`)
  process.exit(1)
}

const refs = [...html.matchAll(/(?:src|href)="([^"]+)"/g)].map((match) => match[1])
const assets = [...new Set(refs.filter((ref) => ref.startsWith(`${base}assets/`)))]

if (assets.length === 0) {
  console.error('No built asset references found in dist/index.html')
  process.exit(1)
}

for (const ref of assets) {
  const relative = ref.slice(base.length).split(/[?#]/, 1)[0]
  const target = normalize(join('dist', relative))
  if (!existsSync(target)) {
    console.error(`Referenced asset is missing: ${ref} -> ${target}`)
    process.exit(1)
  }
}

const slideSource = readFileSync('slides.md', 'utf8')
const delimiters = (slideSource.match(/^---$/gm) || []).length
if (delimiters < 10 || delimiters % 2 !== 0) {
  console.error(`Unexpected slide delimiter count: ${delimiters}`)
  process.exit(1)
}
const slideCount = delimiters / 2
console.log(`OK: ${assets.length} assets present, base "${base}", ${slideCount} slides`)
