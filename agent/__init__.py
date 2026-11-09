"""SystemDesign Problem Set Agent package.

Automated agent that scans trending system design resources, identifies missing problem
sets, generates new problem README files, and creates GitHub PRs.
"""

from agent.core import __version__
from agent.agent_main import SystemDesignAgent

__all__ = ["SystemDesignAgent", "__version__"]
