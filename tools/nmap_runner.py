from tools.base_runner import BaseToolRunner, ToolResult


class NmapRunner(BaseToolRunner):
    def __init__(self, timeout: float = 600.0):
        super().__init__("nmap", needs_root=True, timeout=timeout)

    async def scan(self, target: str) -> ToolResult:
        args = ["-sS", "-sV", "-T4", "--top-ports", "1000", "-oX", "-", target]
        return await self.run(args)
