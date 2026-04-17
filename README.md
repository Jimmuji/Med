<div align="center">

# 🏥 Medical AI Daily

**每天 5 分钟，掌握医疗 AI / 数字健康 / 生物医药最新动态。**

全自动采集 · AI 智能筛选 · 重要性评分 · 每日定时发布

[![Daily Digest](https://github.com/Jimmuji/Med/actions/workflows/daily.yml/badge.svg)](https://github.com/Jimmuji/Med/actions/workflows/daily.yml)
![GitHub last commit](https://img.shields.io/github/last-commit/Jimmuji/Med)
![GitHub stars](https://img.shields.io/github/stars/Jimmuji/Med?style=social)

[**📖 查看最新日报**](daily/) · [**⚙️ 快速部署**](#-快速开始)

</div>

---

## 覆盖领域

```
📰 行业动态   — 产品发布、监管政策、企业新闻
🔬 临床研究   — 临床试验、研究结果、医学进展
🤖 医疗 AI   — 医疗大模型、智能诊断、影像 AI、AI 辅助研发
💊 生物医药   — 新药审批、疗法创新、生物科技融资
```

## 数据来源

| 来源 | 类型 | 语言 |
|------|------|------|
| [STAT News](https://www.statnews.com) | 医疗/生物科技深度报道 | 英文 |
| [Fierce Healthcare](https://www.fiercehealthcare.com) | 数字健康/医疗政策 | 英文 |
| [Fierce Biotech](https://www.fiercebiotech.com) | 生物科技/制药 | 英文 |
| [36Kr 医疗AI](https://36kr.com) | 中国医疗AI动态 | 中文 |
| [36Kr 医疗科技](https://36kr.com) | 中国医疗科技融资 | 中文 |
| [HuggingFace Papers](https://huggingface.co/papers) | 医疗AI学术论文 | 英文 |

## 🚀 快速开始

1. **Fork** 本仓库
2. 进入 **Settings → Secrets → Actions**，添加：`API_KEY`（[DeepSeek](https://platform.deepseek.com/) 或 OpenAI Key）
3. 进入 **Actions**，启用 Workflows
4. 点击 **Run workflow** 手动触发第一次

---

## 项目结构

```
Med/
├── .github/workflows/daily.yml   # 定时任务
├── scripts/
│   ├── main.py                   # 入口
│   ├── sources.py                # 数据源抓取
│   └── summarize.py              # AI 总结
├── daily/                        # 每日日报 Markdown
└── data/                         # 原始抓取数据 JSON
```

---

<div align="center">

**如果觉得有用，欢迎 ⭐ Star！**

</div>
