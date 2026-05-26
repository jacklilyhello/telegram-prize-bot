# Telegram Prize Bot（简化版抽奖发奖机器人）

## 1. 项目介绍
这是一个最小可用的 Telegram 发奖机器人：用户私聊机器人发送 `/start` 后，机器人读取 `message.from_user.id`（Telegram 数字 ID），判断是否在中奖名单里，并按规则发放奖品或返回未中奖提示。

本项目特性：
- 使用 `aiogram 3.x` 实现 Telegram Bot。
- 使用 `SQLite` 持久化领取记录。
- 使用 `python-dotenv` 加载环境变量。
- 支持本地运行和 Docker Compose 部署。

---

## 2. 功能说明
机器人只处理 `/start` 命令，逻辑如下：

1. **私聊场景**
   - 若用户不在 `config.json` 的 `winners` 中：回复 `not_winner_message`。
   - 若用户在 `winners` 中且未领取：
     - 写入 SQLite 领取记录。
     - 按 `winner_message_template` 渲染并发送奖品内容（替换 `{prize}`）。
   - 若用户已领取过：回复 `already_claimed_message`。

2. **群聊场景**
   - 用户在群内发送 `/start`：回复 `请私聊机器人领取奖品。`

3. **防重复领取**
   - 通过 `claims.tg_id PRIMARY KEY` 保证同一用户只能成功写入一次。
   - 即使短时间重复请求，也不会重复发奖。

---

## 3. 项目结构

```text
tg-prize-bot/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   └── handlers.py
├── data/
│   └── .gitkeep
├── .env.example
├── .gitignore
├── config.example.json
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 4. 本地运行方法

```bash
cp .env.example .env
cp config.example.json config.json
pip install -r requirements.txt
python -m app.main
```

> 运行前请确保 Python 版本为 3.11+。

---

## 5. Docker Compose 部署方法

```bash
cp .env.example .env
cp config.example.json config.json
docker compose up -d --build
docker logs -f tg-prize-bot
```

说明：
- `config.json` 通过只读挂载进入容器：`./config.json:/app/config.json:ro`
- `data` 目录挂载到容器用于持久化数据库：`./data:/app/data`
- 容器重启后领取记录不会丢失。

---

## 6. 配置文件说明

### 6.1 `.env`
由 `.env.example` 复制得到。

示例：

```env
BOT_TOKEN=your_telegram_bot_token_here
CONFIG_PATH=config.json
DATABASE_PATH=data/claims.db
```

字段说明：
- `BOT_TOKEN`：从 BotFather 获取。
- `CONFIG_PATH`：中奖配置文件路径，默认 `config.json`。
- `DATABASE_PATH`：SQLite 数据库路径，默认 `data/claims.db`。

### 6.2 `config.json`
由 `config.example.json` 复制得到。

示例：

```json
{
  "not_winner_message": "很抱歉，您没有中奖。",
  "already_claimed_message": "您已经领取过奖品，请勿重复领取。",
  "winner_message_template": "恭喜您中奖！\n\n您的奖品是：\n{prize}",
  "winners": {
    "123456789": "示例奖品A",
    "987654321": "示例奖品B"
  }
}
```

约束：
- `winners` 的 key 必须是可转换为整数的字符串 Telegram ID。
- `winners` 的 value 必须是非空字符串。
- `winner_message_template` 必须包含 `{prize}`。

---

## 7. 如何填写中奖用户 Telegram 数字 ID
在 `config.json` 的 `winners` 中新增条目：

```json
"winners": {
  "123456789": "Kimi API 199 套餐兑换码：AAAA-BBBB-CCCC"
}
```

说明：
- `123456789` 是用户 Telegram 数字 ID（字符串形式）。
- 每个 ID 只能对应一个奖品。
- 不在 `winners` 的用户会收到未中奖提示。

---

## 8. 如何查看日志

### 本地运行日志
直接在终端查看 `python -m app.main` 的输出。

### Docker 日志

```bash
docker logs -f tg-prize-bot
```

日志会记录：
- 机器人启动成功
- 数据库初始化成功
- 用户访问 `/start`
- 用户是否中奖、是否已领取

不会完整输出奖品内容，避免敏感信息泄露。

---

## 9. 如何备份领取数据库

```bash
cp data/claims.db data/claims.db.bak
```

恢复时可将备份文件拷回：

```bash
cp data/claims.db.bak data/claims.db
```

---

## 10. 常见问题

### Q1: 启动时报 `Missing BOT_TOKEN in .env`
请确认 `.env` 已创建且 `BOT_TOKEN` 已填写。

### Q2: 启动时报配置文件错误
请检查：
- `config.json` 是否存在且 JSON 合法。
- 是否包含必需字段：
  - `not_winner_message`
  - `already_claimed_message`
  - `winner_message_template`
  - `winners`
- `winner_message_template` 是否包含 `{prize}`。

### Q3: 用户重复 `/start` 会不会重复发奖？
不会。数据库使用 `tg_id` 主键约束，同一用户只能成功领取一次。

### Q4: 群里发送 `/start` 为什么没发奖？
本项目按要求主要支持私聊发奖。群内会提示：`请私聊机器人领取奖品。`

### Q5: 如何查看领取记录？

```bash
sqlite3 data/claims.db
SELECT * FROM claims;
```

