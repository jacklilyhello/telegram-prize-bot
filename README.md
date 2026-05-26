# Telegram Prize Bot（简化版抽奖发奖机器人）

## 1. 项目简介
这是一个最小可用的 Telegram 发奖机器人。用户私聊机器人发送 `/start` 后，机器人读取 `message.from_user.id`，根据 `config.json` 的中奖名单判断并发放对应奖品。

## 2. 功能说明
- 仅处理 `/start`。
- 私聊中：
  - 未中奖：回复 `not_winner_message`
  - 首次中奖领取：写入 SQLite 并发送奖品消息
  - 重复领取：回复 `already_claimed_message`
- 群聊中：回复 `请私聊机器人领取奖品。`
- 使用 SQLite `tg_id PRIMARY KEY` 防止重复领取。

## 3. 文件结构
```text
tg-prize-bot/
├── app/
│   ├── __init__.py
│   ├── claim_service.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   └── handlers.py
├── tests/
│   ├── test_config.py
│   ├── test_database.py
│   └── test_claim_logic.py
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

## 4. 本地运行
```bash
cp .env.example .env
cp config.example.json config.json
pip install -r requirements.txt
python -m app.main
```

## 5. Docker Compose 运行
```bash
cp .env.example .env
cp config.example.json config.json
docker compose up -d --build
docker logs -f tg-prize-bot
```

## 6. 配置说明
### `.env`
```env
BOT_TOKEN=your_telegram_bot_token_here
CONFIG_PATH=config.json
DATABASE_PATH=data/claims.db
```

### `config.json`
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

## 7. 如何填写中奖用户 TG 数字 ID
在 `config.json` 的 `winners` 中添加条目，key 为字符串数字 ID，value 为奖品文本。

## 8. 如何查看日志
- 本地：直接查看 `python -m app.main` 终端输出
- Docker：`docker logs -f tg-prize-bot`

## 9. 如何查看 SQLite 领取记录
```bash
sqlite3 data/claims.db
SELECT * FROM claims;
```

## 10. 如何备份数据库
```bash
cp data/claims.db data/claims.db.bak
```

## 11. 常见问题
- 启动报 `Missing BOT_TOKEN`：检查 `.env` 或环境变量。
- 重复领取：系统会返回已领取提示，属正常行为。

## 12. 测试命令
```bash
python -m compileall app
python -m pytest -q
```

## 安全提醒
- 不要提交 `.env`
- 不要提交 `config.json`
- 不要提交真实奖品兑换码
- `BOT_TOKEN` 仅通过环境变量或 `.env` 提供
