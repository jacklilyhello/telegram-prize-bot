# 任务：从空仓库开发一个简化版 Telegram 抽奖发奖机器人
## 一、项目目标
请从一个空仓库开始，开发一个简化版 Telegram Bot，用于抽奖活动后的自动发奖。
机器人逻辑非常简单：
用户私聊机器人并发送 `/start` 后，机器人读取用户的 Telegram 数字 ID，也就是 `message.from_user.id`，然后判断该用户是否在中奖名单配置文件中。
- 如果用户 ID 在中奖名单中：
  - 给该用户发送对应的预设奖品内容
  - 每个中奖用户只能领取一次
  - 一个用户只能领取自己对应的一个奖品
  - 已领取后再次 `/start`，只能看到“已领取过”的提示，不能重复发奖
- 如果用户 ID 不在中奖名单中：
  - 给用户发送固定的未中奖文案，例如：`很抱歉，您没有中奖。`
这是一个最小可用版本，不需要复杂后台，不需要网页管理面板，不需要支付系统，不需要 Emby API 对接。
---
## 二、技术栈要求
请使用以下技术栈：
- Python 3.11+
- aiogram 3.x
- SQLite
- python-dotenv
- Docker
- Docker Compose
要求项目可以本地运行，也可以通过 Docker Compose 部署运行。
---
## 三、核心功能要求
### 1. `/start` 私聊触发
机器人只需要处理 `/start` 命令。
用户向机器人私聊发送：
```text
/start

机器人获取：

message.from_user.id

该值是 Telegram 数字 ID。

然后进入判断流程。

⸻

2. 中奖名单配置

中奖名单必须从 config.json 读取，不允许写死在代码中。

配置文件示例：

{
  "not_winner_message": "很抱歉，您没有中奖。",
  "already_claimed_message": "您已经领取过奖品，请勿重复领取。",
  "winner_message_template": "恭喜您中奖！\n\n您的奖品是：\n{prize}",
  "winners": {
    "123456789": "Kimi API 199 套餐兑换码：AAAA-BBBB-CCCC",
    "987654321": "Kimi API 199 套餐兑换码：DDDD-EEEE-FFFF"
  }
}

说明：

* winners 的 key 是 Telegram 数字 ID，必须是字符串形式
* winners 的 value 是该用户对应的奖品内容
* 一个 Telegram ID 只能对应一个奖品
* 一个用户不能领取两个奖品
* 不在 winners 里面的用户就是未中奖用户

⸻

3. 未中奖逻辑

如果用户的 Telegram 数字 ID 不在 config.json 的 winners 中，直接回复：

很抱歉，您没有中奖。

实际内容应读取配置文件中的：

"not_winner_message"

⸻

4. 中奖发奖逻辑

如果用户的 Telegram 数字 ID 在 winners 中，则继续判断是否已经领取过。

如果没有领取过：

1. 从配置文件中找到该用户对应的奖品
2. 将领取记录写入 SQLite
3. 给用户发送中奖消息

中奖消息使用配置文件中的模板：

"winner_message_template": "恭喜您中奖！\n\n您的奖品是：\n{prize}"

其中 {prize} 替换成该用户对应的奖品内容。

例如：

恭喜您中奖！
您的奖品是：
Kimi API 199 套餐兑换码：AAAA-BBBB-CCCC

⸻

5. 防重复领取

必须使用 SQLite 持久化记录领取状态。

建议表结构：

CREATE TABLE IF NOT EXISTS claims (
  tg_id INTEGER PRIMARY KEY,
  prize TEXT NOT NULL,
  claimed_at TEXT NOT NULL
);

要求：

* tg_id 必须是主键
* 同一个 tg_id 只能写入一次
* 机器人重启后，领取状态不能丢失
* Docker 容器重启后，领取状态不能丢失
* 即使用户短时间内多次发送 /start，也不能重复发奖

如果用户已经领取过，再次 /start 时回复：

您已经领取过奖品，请勿重复领取。

实际内容应读取配置文件中的：

"already_claimed_message"

⸻

四、配置文件要求

项目根目录需要包含：

.env.example
config.example.json

1. .env.example

内容示例：

BOT_TOKEN=your_telegram_bot_token_here
CONFIG_PATH=config.json
DATABASE_PATH=data/claims.db

说明：

* 实际运行时用户复制 .env.example 为 .env
* BOT_TOKEN 从 BotFather 获取
* CONFIG_PATH 默认是 config.json
* DATABASE_PATH 默认是 data/claims.db

⸻

2. config.example.json

内容示例：

{
  "not_winner_message": "很抱歉，您没有中奖。",
  "already_claimed_message": "您已经领取过奖品，请勿重复领取。",
  "winner_message_template": "恭喜您中奖！\n\n您的奖品是：\n{prize}",
  "winners": {
    "123456789": "示例奖品A",
    "987654321": "示例奖品B"
  }
}

说明：

* 实际运行时用户复制 config.example.json 为 config.json
* 真实奖品只写入 config.json
* 不要把真实奖品提交到 GitHub

⸻

五、项目结构要求

请生成以下项目结构：

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

说明：

* app/main.py：机器人入口
* app/config.py：读取 .env 和 config.json
* app/database.py：SQLite 初始化、查询、写入
* app/handlers.py：处理 /start
* data/：用于存放 SQLite 数据库文件
* .gitignore：必须忽略 .env、config.json、data/*.db

⸻

六、代码实现要求

1. 配置校验

启动时必须校验：

* .env 中是否存在 BOT_TOKEN
* config.json 是否存在
* config.json 是否是合法 JSON
* 是否包含以下字段：
    * not_winner_message
    * already_claimed_message
    * winner_message_template
    * winners
* winners 必须是 object/dict
* winner_message_template 必须包含 {prize}
* winners 的 key 必须可以转换为整数 Telegram ID
* winners 的 value 必须是非空字符串

如果配置错误，启动时应直接报错并退出，不要静默失败。

⸻

2. 日志要求

请使用 Python 标准 logging。

日志要求：

* 记录机器人启动成功
* 记录数据库初始化成功
* 记录用户访问 /start
* 记录用户是否中奖
* 记录用户是否已领取
* 不要在日志中完整打印奖品内容，避免泄露兑换码

可以记录类似：

User 123456789 is winner
User 123456789 claimed prize
User 123456789 already claimed
User 111111111 is not winner

不要记录：

User 123456789 prize is AAAA-BBBB-CCCC

⸻

3. 私聊限制

/start 应主要用于私聊。

如果用户在群组中发送 /start，机器人可以回复：

请私聊机器人领取奖品。

或者直接忽略。

建议配置在代码中固定为：

请私聊机器人领取奖品。

⸻

4. SQLite 并发安全

领取奖品时必须避免重复写入。

建议方式：

* tg_id 设置为 PRIMARY KEY
* 写入时使用事务
* 捕获 sqlite3.IntegrityError
* 如果插入失败，说明已经领取过，返回已领取提示

核心逻辑应该是：

1. 查询是否已领取
2. 如果未领取，尝试插入
3. 如果插入成功，发送奖品
4. 如果插入失败，发送已领取提示

⸻

七、Docker 要求

1. Dockerfile

要求：

* 使用 Python 3.11 slim 镜像
* 安装 requirements
* 工作目录为 /app
* 启动命令运行 bot

⸻

2. docker-compose.yml

要求：

services:
  tg-prize-bot:
    build: .
    container_name: tg-prize-bot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./config.json:/app/config.json:ro
      - ./data:/app/data

说明：

* config.json 只读挂载
* data 挂载出来，保证 SQLite 数据持久化
* 容器重启不丢失领取记录

⸻

八、README 要求

请编写完整 README.md，内容包括：

1. 项目介绍
2. 功能说明
3. 项目结构
4. 本地运行方法
5. Docker Compose 部署方法
6. 配置文件说明
7. 如何填写中奖用户 Telegram 数字 ID
8. 如何查看日志
9. 如何备份领取数据库
10. 常见问题

README 中需要包含以下命令：

本地运行

cp .env.example .env
cp config.example.json config.json
pip install -r requirements.txt
python -m app.main

Docker 运行

cp .env.example .env
cp config.example.json config.json
docker compose up -d --build
docker logs -f tg-prize-bot

查看数据库

sqlite3 data/claims.db
SELECT * FROM claims;

备份数据库

cp data/claims.db data/claims.db.bak

⸻

九、不要实现的功能

请不要实现以下功能：

* 不要做网页后台
* 不要做管理员面板
* 不要做支付系统
* 不要对接 Emby API
* 不要做邀请码自动生成
* 不要做复杂权限系统
* 不要做群内抽奖
* 不要做多语言
* 不要做 Redis
* 不要做 PostgreSQL
* 不要做 MySQL

本项目只做最小可用发奖机器人。

⸻

十、最终交付要求

请完成以下文件：

app/__init__.py
app/main.py
app/config.py
app/database.py
app/handlers.py
data/.gitkeep
.env.example
.gitignore
config.example.json
requirements.txt
Dockerfile
docker-compose.yml
README.md

完成后请确保：

python -m app.main

可以正常启动。

并确保：

docker compose up -d --build

可以正常启动。

⸻

十一、验收标准

项目完成后应满足以下测试场景：

场景 1：未中奖用户

配置文件中没有该 Telegram ID。

用户发送：

/start

机器人回复：

很抱歉，您没有中奖。

⸻

场景 2：中奖用户首次领取

配置文件中存在该 Telegram ID，且数据库中没有领取记录。

用户发送：

/start

机器人回复：

恭喜您中奖！
您的奖品是：
对应奖品内容

并且数据库中新增一条领取记录。

⸻

场景 3：中奖用户重复领取

配置文件中存在该 Telegram ID，但数据库中已经有领取记录。

用户发送：

/start

机器人回复：

您已经领取过奖品，请勿重复领取。

不能再次发送奖品。

⸻

场景 4：机器人重启后重复领取

中奖用户已经领取过。

重启 Docker 容器后，该用户再次发送：

/start

机器人仍然回复：

您已经领取过奖品，请勿重复领取。

说明 SQLite 持久化正常。

⸻

场景 5：群聊中发送 /start

用户在群聊发送：

/start

机器人回复：

请私聊机器人领取奖品。

或者忽略。

推荐回复提示私聊机器人。

⸻

十二、开发质量要求

请保持代码结构清晰，函数职责单一。

要求：

* 有类型标注
* 有必要的异常处理
* 不泄露奖品内容到日志
* 配置错误时明确报错
* README 能让普通用户照着部署
* Docker Compose 适合直接上线使用

请直接开始实现，不需要再询问需求。

