# Development

## 文件结构

```text
data/
  laptops.json      # 页面使用的机型数据
  *.et              # 本地源表格，默认不提交
.github/
  workflows/pages.yml
scripts/
  extract_guide.py  # 从源指南中尝试抽取文本/表格信息
index.html          # 静态可视化页面
```

## 验证

```powershell
.\scripts\check.ps1
npm test
```

## 刷新数据

```powershell
.\.venv\Scripts\python.exe .\scripts\extract_guide.py
```

## 约束

- 不提交源 `.et` 大文件。
- 页面应保持纯静态，方便 GitHub Pages 托管。
- 价格会随时间波动，页面必须标注采集日期。
