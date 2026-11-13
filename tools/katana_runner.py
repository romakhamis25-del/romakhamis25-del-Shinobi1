from tools.base_runner import BaseToolRunner, ToolResult


class KatanaRunner(BaseToolRunner):
    def __init__(self, timeout: float = 300.0):
        super().__init__("katana", needs_root=False, timeout=timeout)

    async def scan(self, target: str) -> ToolResult:
        args = ["-u", target, "-d", "3", "-jc", "-silent", "-jsonl"]
        return await self.run(args)
