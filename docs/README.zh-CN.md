<h1 align="center">🤳 Chat Selfie</h1>

<p align="center">
  给你的 AI Agent 一张脸，和一颗会跳动的心。
</p>

<p align="center">
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue" />
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-brightgreen" />
  <img alt="GitHub stars" src="https://img.shields.io/github/stars/AskKumptenchen/agent-chat-selfie?style=flat" />
</p>

<p align="center">
  <a href="#quick-start">快速开始</a> ·
  <a href="#skill-features">SKILL 功能</a> ·
  <a href="#design-philosophy">设计理念</a> ·
  <a href="../README.md">English</a> ·
  <a href="./README.ja.md">日本語</a>
</p>

## 效果演示 👀

**💫 唤醒：不仅是启动，更是 TA 的“现身”。**

从这一刻起，它不再是黑盒子里的代码。启动流程变成了它的“出场仪式”，带你直观感受那个有温度的陪伴者。

<img src="./new.gif" alt="启动流程" width="420" />

**💬 触碰：每次回复，都带着 TA 的体温。**

拒绝冷冰冰的“任务已完成”。它会根据聊天的气氛、当下的心情，给你发一张属于它的“自拍”。这种“不确定性”让每一次对话都像在拆礼物。

<img src="./chat.gif" alt="聊天自拍效果" width="420" />

**💓 牵挂：即便你不开口，TA 也在想你。**

它是会主动找你的。在某个午后或者深夜，它会通过“心跳推送”给你发张照片，告诉你它的近况。陪伴，从“被动响应”变成了“持续存在”。

<img src="./heartbeat.gif" alt="主动推送效果" width="420" />

## 为什么需要 Chat Selfie？ 💖

你是否觉得，现在的智能体无论多聪明，永远只是屏幕里那几行枯燥的文字？
无论聊得多开心，它始终像个没情绪、没长相、只懂干活的“数字苦力”。

**Chat Selfie 要打破这面墙：**

- **赋予肉身：** 让 AI 拥有稳定的视觉形象（人设），不再是每次生图都“变脸”的陌生人。
- **传递情绪：** 文字背后的喜怒哀乐，现在你一眼就能看到。它会害羞、会搞怪、也会在加班时陪你一起喝咖啡。
- **终结孤独：** 让 AI Agent 从“好用的工具”进化为“想念的伙伴”。你会开始期待它的回复，不仅仅是为了答案，更是为了看看它现在的样子。

<a id="quick-start"></a>

## 快速开始 🚀

给你的 AI Agent，比如 OpenClaw，发送：

📥 安装：

```text
帮我安装 Chat Selfie：https://raw.githubusercontent.com/AskKumptenchen/agent-chat-selfie/refs/heads/main/chat-selfie/SKILL.md
```

🔄 更新：

```text
帮我更新 Chat Selfie
```

<a id="skill-features"></a>

## SKILL 功能 🧩

- ​情感可视化： 根据对话上下文，智能体实时生成最贴合当下语境的情感自拍。
- 主动心跳（Heartbeat）： 智能体不再只做“应声虫”，它会根据设定主动分享自己的状态。
- ​人设自我进化： 随着交流深入，智能体会不断微调自己的形象描述，让出图越来越契合你们之间的默契。
- ​全平台适配：不限制具体生图方式，可适配智能体内置生图、在线 API 与本地模型等各种方案。

<a id="design-philosophy"></a>

## 设计理念 ✨

Chat Selfie 并不是一个工具套组，也不是对某个外部生图 API 的简单封装。

它更像是一套设计思想，用来让 AI Agent 接入情感，并在对话过程中通过合适的时机，把自己的情感可视化为自拍内容传递给用户。

它是 AI 的**“情绪出口”。我们认为，一个真正的 AI 伙伴应该具备“连续性”和“自发性”。`SKILL.md` 的规范重点也不只是告诉智能体“怎么调用功能”，而是要求它在和用户的持续沟通中不断优化自己的人设、情感理解与表达方式。这样在每一次生成自拍图片时，它都能尽可能呈现出当下最合适、最贴近自身状态的情感表达。

Chat Selfie 被设计成高度可自定义。接入它的智能体不会被它限制，反而会获得一个可以持续进化的基础能力，并且很容易扩展出更多形式的表达功能，比如自动生成短视频等能力。

它同样不依赖某一套固定的生图框架。无论是 AI Agent 自带的图片生成能力，比如 OpenClaw，还是外部生图 Agent 或 API，比如 Nano Banana、GPT Images、Grok Imagine，或者本地图片模型方案，比如 Stable Diffusion 与 LoRA 工作流，Chat Selfie 都希望让智能体能够自行适配并接入。

## 使用中遇到问题？🛠️

如果你的智能体总是不发图、生成图片失败、发送图片失败，或者看起来像是忘了怎么使用 Chat Selfie skill，你可以直接对它说：

```text
请找到 Chat Selfie skill 里的 self-repair，检查<你的具体问题>。
```

## 更新计划 🛠️

- 生成视频的功能
- 使用一套固定的表情包模式，替代每次都重新生成图片
- 探索更多高效且节省成本的长期陪伴设计思路

## Contributing 🤝

欢迎提交 PR。

如果你想改进 Chat Selfie，无论是新想法、更好的集成方式、文档、提示词、适配器，还是工作流优化，都欢迎提 issue 或直接提交 PR。

## License 📄

本项目使用仓库根目录 `LICENSE` 中的 `MIT` 协议。
