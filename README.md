# MCP-TEST

三、如何运行
python3 mini_mcp_server.py

四、如何验证（非常重要）
1️⃣ 模型发现能力
curl http://localhost:8080/capabilities


返回的是给模型看的能力说明书。

2️⃣ 模型调用能力
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "action": "user_status_query",
    "params": {
      "userId": "1001"
    }
  }'


返回：

{
  "type": "context_append",
  "content": "用户 1001 当前状态为：已激活"
}


这一步，闭环完成。
