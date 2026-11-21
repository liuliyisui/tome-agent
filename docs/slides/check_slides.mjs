// Slidev 版幻灯片 + GitHub Actions 工作流的静态自检
// 用法：node check_slides.mjs   （在 slides/slidev 下执行）
import { readFileSync, readdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { parse } from 'yaml'

const here = resolve(import.meta.dirname)
const root = resolve(here, '..', '..')  // docs/slides → 仓库根
// 文件带 UTF-8 BOM（保证 Windows 编辑器不乱码），解析前先去掉
const raw = readFileSync(join(here, 'slides.md'), 'utf8').replace(/^\uFEFF/, '')
const lines = raw.split(/\r?\n/)

const seps = lines.filter(l => l.trim() === '---').length
// 每页都写了 frontmatter，所以每页贡献 2 个 ---，页数 = 分隔符总数 / 2
console.log(`--- 分隔符: ${seps}  → 页数 ${seps / 2}`)
console.log(`H1 标题: ${lines.filter(l => l.startsWith('# ')).length} 个（封面用 div 排版，无 H1）`)

const must = [
  '1.1.1 使命', '1.1.2 口号', '1.1.3 目标用户', '1.1.4 如何获得用户',
  '1.1.5 团队优势', '1.1.6 如何做到差异化',
  '1.2 产品定义', '1.2.1 解决的问题', '1.2.2 对客户的价值', '1.2.3 解决方案',
  '需求原则', '信息原则', '创新原则', '系统原则', '收敛原则', '优化原则',
  '继承原则', '效益原则', '时间原则', '定量原则', '简化原则', '审核原则',
]
const missing = must.filter(m => !raw.includes(m))
console.log('缺少的小节/原则:', missing.length ? missing : '无')

const wfDir = join(root, '.github', 'workflows')
for (const f of readdirSync(wfDir).filter(f => f.endsWith('.yml'))) {
  const doc = parse(readFileSync(join(wfDir, f), 'utf8'))
  const jobs = Object.keys(doc.jobs ?? {}).join(', ')
  console.log(`OK ${f} → name=${JSON.stringify(doc.name)} jobs=[${jobs}]`)
}
