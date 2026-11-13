from tools.base_runner import BaseToolRunner, ToolResult


class SqlmapRunner(BaseToolRunner):
    def __init__(self, timeout: float = 900.0):
        super().__init__("sqlmap", needs_root=False, timeout=timeout)

    async def scan(self, target: str) -> ToolResult:
        args = [
            "-u", target, "--batch",
            "--level=2", "--risk=2",
            "--threads=5", "--timeout=10",
            "--tamper=space2comment",
        ]
        return await self.run(args)
