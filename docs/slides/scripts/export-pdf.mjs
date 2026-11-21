import { spawnSync } from 'node:child_process'
import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { PDFDocument } from 'pdf-lib'

const pagesDir = join('dist', '.pdf-pages')
const output = join('dist', 'tome-agent-slides.pdf')
const slideFile = process.env.SLIDE_FILE || 'slides.md'
const slidevBin = join('node_modules', '@slidev', 'cli', 'bin', 'slidev.mjs')

rmSync(pagesDir, { force: true, recursive: true })
mkdirSync(pagesDir, { recursive: true })

console.log('Rendering slides to PNG pages...')
const result = spawnSync(
  process.execPath,
  [
    slidevBin,
    'export',
    slideFile,
    '--format',
    'png',
    '--per-slide',
    '--output',
    pagesDir,
    '--scale',
    '2',
    '--timeout',
    '180000',
    '--wait',
    '500',
  ],
  { stdio: 'inherit', env: process.env },
)

if (result.error) {
  console.error(result.error)
  process.exit(1)
}
if (result.status !== 0) {
  console.error(`Slidev PNG export failed with exit code ${result.status}`)
  process.exit(result.status ?? 1)
}

const files = readdirSync(pagesDir)
  .filter((name) => name.endsWith('.png'))
  .sort((a, b) => Number.parseInt(a, 10) - Number.parseInt(b, 10))

if (files.length === 0) {
  console.error(`No PNG pages found in ${pagesDir}`)
  process.exit(1)
}

console.log(`Building PDF from ${files.length} pages...`)
const pdf = await PDFDocument.create()
pdf.setTitle('Tome Agent · 让一个点子，长成一部自洽的长篇')
pdf.setAuthor('宇宙无敌暴龙战士（查军益 / 秦宗鑫 / 谭钧浩 / 周涛）')
pdf.setCreator('Slidev + pdf-lib')
pdf.setProducer('GitHub Actions')

for (const file of files) {
  const bytes = readFileSync(join(pagesDir, file))
  const image = await pdf.embedPng(bytes)
  const page = pdf.addPage([960, 540])
  page.drawImage(image, { x: 0, y: 0, width: 960, height: 540 })
}

mkdirSync('dist', { recursive: true })
writeFileSync(output, await pdf.save())
rmSync(pagesDir, { force: true, recursive: true })

if (!existsSync(output)) {
  console.error(`PDF was not written to ${output}`)
  process.exit(1)
}

console.log(`PDF written to ${output}`)
