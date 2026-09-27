# DAIRA Dynamic Trace Skill

使用这个 skill 前，需要先配置模型接口。将 `.env.example` 复制为当前目录下的 `.env`，然后填写模型 API key、接口地址和模型名称：

```bash
cp .env.example .env
```

`.env` 示例：

```ini
OPENAI_API_KEY=replace-with-your-openai-api-key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL_NAME=deepseek-chat
```

也可以配置 OpenAI 或其他兼容 OpenAI Chat Completions API 的服务：

```ini
OPENAI_API_KEY=replace-with-your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL_NAME=replace-with-your-model
```

环境变量优先于 `.env` 文件中的配置。真实 `.env` 不要提交到 Git。
