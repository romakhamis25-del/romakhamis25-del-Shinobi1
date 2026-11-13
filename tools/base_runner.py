"""
SHINOBI :: Base Tool Runner
Safely executes external security tools with optional sudo elevation.
"""

import asyncio
import logging
import shlex
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class ToolResult:
    tool: str
    success: bool
    stdout: str
    stderr: str
    returncode: int
    duration: float


class BaseToolRunner(ABC):
    """
    • Uses list-form subprocess (no shell injection).
    • Optional sudo via `sudo -n` (non-interactive).
    • Never raises on tool failure — returns ToolResult(success=False).
    """

    def __init__(self, binary: str, needs_root: bool = False, timeout: float = 300.0):
        self.binary = binary
        self.needs_root = needs_root
        self.timeout = timeout
        self.logger = logging.getLogger(f"shinobi.tool.{binary}")

    def _build_cmd(self, args: List[str]) -> List[str]:
        cmd = [self.binary] + args
        if self.needs_root:
            cmd = ["sudo", "-n"] + cmd
        return cmd

    async def run(self, args: List[str]) -> ToolResult:
        cmd = self._build_cmd(args)
        self.logger.info(f"Executing: {' '.join(shlex.quote(c) for c in cmd)}")

        start = time.monotonic()
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout_b, stderr_b = await asyncio.wait_for(
                    proc.communicate(), timeout=self.timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                self.logger.error(f"{self.binary} timed out after {self.timeout}s")
                return ToolResult(
                    self.binary, False, "", "timeout", -1, time.monotonic() - start
                )

            duration = time.monotonic() - start
            result = ToolResult(
                tool=self.binary,
                success=(proc.returncode == 0),
                stdout=stdout_b.decode("utf-8", errors="replace"),
                stderr=stderr_b.decode("utf-8", errors="replace"),
                returncode=proc.returncode,
                duration=duration,
            )
            if not result.success:
                self.logger.warning(
                    f"{self.binary} exited {proc.returncode}: {result.stderr[:200]}"
                )
            return result

        except FileNotFoundError:
            self.logger.error(f"Binary not found: {self.binary}")
            return ToolResult(self.binary, False, "", "binary_not_found", -1, 0.0)
        except Exception as exc:  # noqa: BLE001
            self.logger.error(f"Unexpected error running {self.binary}: {exc}")
            return ToolResult(self.binary, False, "", str(exc), -1, 0.0)

    @abstractmethod
    async def scan(self, target: str) -> ToolResult:
        ...
