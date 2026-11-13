from tools.base_runner import BaseToolRunner, ToolResult


class NucleiRunner(BaseToolRunner):
    def __init__(self, timeout: float = 900.0):
        super().__init__("nuclei", needs_root=False, timeout=timeout)

    async def scan(self, target: str) -> ToolResult:
        args = [
            "-u", target,
            "-severity", "low,medium,high,critical",
            "-jsonl", "-silent",
        ]
        return await self.run(args)
