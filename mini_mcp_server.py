from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse

HOST = "0.0.0.0"
PORT = 8080

# ===== 模拟业务数据（现实世界） =====
USER_DB = {
    "1001": "已激活",
    "1002": "已冻结",
    "1003": "未注册"
}


class McpHandler(BaseHTTPRequestHandler):

    # ---------- 基础设施 ----------
    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    # ---------- HTTP 路由 ----------
    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/capabilities":
            self.handle_capabilities()
        else:
            self._send_json({"error": "NOT_FOUND"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/invoke":
            self.handle_invoke()
        else:
            self._send_json({"error": "NOT_FOUND"}, 404)

    # ---------- MCP 核心 ----------
    def handle_capabilities(self):
        """
        1. 告诉模型：我有什么能力
        """
        self._send_json({
            "capabilities": [
                {
                    "name": "user_status_query",
                    "description": "根据用户ID查询用户当前状态",
                    "input_schema": {
                        "userId": "string"
                    },
                    "output_schema": {
                        "status": "string"
                    }
                }
            ]
        })

    def handle_invoke(self):
        """
        2. 模型调用能力
        """
        req = self._read_json()
        action = req.get("action")
        params = req.get("params", {})

        if action == "user_status_query":
            self.handle_user_status(params)
        else:
            self._send_json({
                "error": {
                    "code": "UNKNOWN_ACTION",
                    "message": f"未知能力：{action}"
                }
            }, 400)

    def handle_user_status(self, params):
        """
        3. 执行业务 + 4. 结果回注
        """
        user_id = params.get("userId")

        if not user_id:
            self._send_json({
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "缺少 userId"
                }
            }, 400)
            return

        # ---- 真实业务执行（这里是模拟 DB） ----
        status = USER_DB.get(user_id, "未知用户")

        # ---- MCP 回注：给模型看的“语义结果” ----
        self._send_json({
            "type": "context_append",
            "content": f"用户 {user_id} 当前状态为：{status}"
        })


def run():
    server = HTTPServer((HOST, PORT), McpHandler)
    print(f"MCP Server running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()
