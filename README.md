# 高考后游戏本选购可视化

一个给“小白买游戏本”使用的静态选购页面。它基于金山文档云端表格《小白必读》购机指南，将其中“甜品砖头”和“高端砖头”两个分区的机型整理成可筛选、可比较、可直接发给家人看的网页。

在线页面：

```text
https://wychuang.github.io/gaokao-laptop-guide/
```

仓库地址：

```text
https://github.com/wychuang/gaokao-laptop-guide
```

## 功能

- **筛选器**：按类别、价位、品牌、显卡、屏幕尺寸、内存和 OLED 偏好筛选。
- **坐标图**：用“参考价位 x 重量”展示每台机器的位置，点的大小代表厚度。
- **外观预览**：鼠标悬停在坐标点上显示机型外观图。
- **机型卡片**：按指南顺序列出规格、亮点、注意点和短板。
- **静态部署**：无后端、无数据库，可直接部署到 GitHub Pages。

## 数据来源

核心机型数据来自金山文档云端表格：

```text
https://www.kdocs.cn/l/chzEHrH90jRz
```

本项目使用流程是：先将这份云端表格下载为 `.et` 文件，放入 `data/` 目录，再通过脚本抽取“甜品砖头”和“高端砖头”两个工作表，生成页面使用的结构化数据 `data/laptops.json`。

外观图来自页面底部列出的公开网页来源。项目不声称与任何品牌、平台或原指南作者有关。

价格说明：

- 页面中的价格使用指南里的价位段，例如 `9-11k`、`20-30k`。
- 这些价位没有计算神券、国补、地区仓、缺货、临时促销或平台价格波动。
- 源表格目前没有逐机型实时成交价；没有人工核价时，坐标图使用价位段中值作为“坐标价”，并在卡片里标明口径。
- 如果要展示更精确的当日价格，可以复制 `data/price-overrides.example.json` 为 `data/price-overrides.json`，填入 `priceCny` 后重新运行抽取脚本。
- 买之前仍然需要重新核对当天价格和售后政策。

## 本地预览

```powershell
npm install
npm run serve
```

然后打开：

```text
http://127.0.0.1:4173/
```

也可以不用 npm：

```powershell
python -m http.server 4173 --bind 127.0.0.1
```

## 刷新数据

从金山文档下载最新版 `.et` 表格，放到 `data/` 目录下，然后运行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\scripts\extract_guide.py
```

脚本会优先读取 `data/*.et`，并重新生成 `data/laptops.json`。如果云端表格结构发生变化，可能需要同步调整 `scripts/extract_guide.py` 的列映射。

可选：人工核价。

```powershell
Copy-Item .\data\price-overrides.example.json .\data\price-overrides.json
notepad .\data\price-overrides.json
.\.venv\Scripts\python.exe .\scripts\extract_guide.py
```

填写 `priceCny` 后，页面的坐标点、卡片价格和价格排序会使用人工核价；没有填写的机型仍使用价位段中值。

## 验证

```powershell
.\scripts\check.ps1
npm test
```

`check.ps1` 会确认静态入口和 JSON 数据可读；Playwright smoke test 会确认页面能加载 34 个机型、坐标点和筛选器。

## 部署

项目已经包含 GitHub Pages Actions 工作流：

```text
.github/workflows/pages.yml
```

当前仓库已经启用 GitHub Pages。之后每次推送 `main` 分支都会自动发布到：

```text
https://wychuang.github.io/gaokao-laptop-guide/
```

## 仓库约定

下载得到的 `.et` 表格默认不提交到 GitHub。它体积较大，而且只是云端表格的本地副本；公开仓库只提交页面所需的结构化数据 `data/laptops.json`。

更多 git 安排见 [GIT_PLAN.md](GIT_PLAN.md)。
