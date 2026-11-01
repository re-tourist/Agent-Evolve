"""Thin pinned τ-bench adapter. No copied tasks, scoring algorithm or database manager."""

import hashlib
import os
import subprocess
from pathlib import Path
from unittest.mock import patch

from agent_evolve.baseline import TAU_SHA, Prompt, ProviderError, SimulatorError


def make_agent(prompt: Prompt, tools, model: str, model_args: dict, *, scripted: bool):
    """Instance-local instructions; official policy bytes are never configurable."""
    from tau2.agent.llm_agent import LLMAgent
    from tau2.data_model.message import AssistantMessage, ToolCall

    class PromptAgent(LLMAgent):
        @property
        def system_prompt(self):
            return prompt.system

        def generate_next_message(self, message, state):
            if not scripted:
                # Construction seam for a reviewed future live backend, unreachable by M2-A CLI.
                return super().generate_next_message(message, state)
            state.messages.append(message)
            if getattr(self, "_scripted_calls", 0) == 0:
                response = AssistantMessage(
                    role="assistant",
                    tool_calls=[
                        ToolCall(
                            id="scripted-inspect",
                            name="get_order_details",
                            arguments={"order_id": "#W2378156"},
                        )
                    ],
                )
            else:
                response = AssistantMessage(
                    role="assistant", content="Scripted inspection complete."
                )
            state.messages.append(response)
            self._scripted_calls = getattr(self, "_scripted_calls", 0) + 1
            return response, state

    return PromptAgent(
        tools=tools, domain_policy=prompt.policy, llm=model, llm_args=dict(model_args)
    )


def build_live_components(config, task, prompt):
    """Construction-only seam: configure official participants without running/generating.

    M2-A execute() always rejects live before this seam can be reached by the CLI.
    Actual provider/budget activation remains a separately reviewed M2-B change.
    """
    from tau2.data_model.tasks import Task
    from tau2.orchestrator.orchestrator import Orchestrator
    from tau2.runner import build_environment, build_user

    task = Task.model_validate(task)
    environment = build_environment("retail")
    if environment.get_policy() != prompt.policy:
        raise ValueError("Official Policy mismatch")
    return Orchestrator(
        domain="retail",
        agent=make_agent(
            prompt,
            environment.get_tools(),
            config.agent_model,
            config.agent_args or {},
            scripted=False,
        ),
        user=build_user(
            "user_simulator",
            environment,
            task,
            llm=config.user_model,
            llm_args=dict(config.user_args or {}),
        ),
        environment=environment,
        task=task,
        max_steps=config.max_steps,
        max_errors=2,
        seed=config.seed,
    )


class TauBackend:
    def __init__(self, checkout):
        if not checkout:
            raise ValueError("tau_checkout required for the pinned official backend")
        self.checkout = Path(checkout).resolve()
        sha = subprocess.check_output(
            ["git", "-C", str(self.checkout), "rev-parse", "HEAD"], text=True, timeout=5
        ).strip()
        changed = subprocess.check_output(
            ["git", "-C", str(self.checkout), "status", "--porcelain", "--untracked-files=no"],
            text=True,
            timeout=5,
        ).strip()
        if sha != TAU_SHA or changed:
            raise ValueError(
                "Official checkout must match the pin and have no tracked modifications"
            )
        data = self.checkout / "data"
        with patch.dict(os.environ, {"TAU2_DATA_DIR": str(data)}):
            from tau2 import __file__ as installed_source
            from tau2.runner import build_environment
            from tau2.utils.utils import DATA_DIR

        if not Path(installed_source).resolve().is_relative_to(self.checkout):
            raise ValueError("Installed tau2 must be the audited editable checkout")
        if Path(DATA_DIR).resolve() != data:
            raise ValueError(
                "tau2 already imported with a different data root; start a fresh process"
            )
        self.policy = build_environment("retail").get_policy()
        self.data_identity = {
            p.relative_to(data).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((data / "tau2/domains/retail").rglob("*"))
            if p.is_file()
        }

    def tasks(self, ids):
        from tau2.runner import get_tasks

        tasks = get_tasks("retail", task_ids=list(ids))
        by_id = {task.id: task for task in tasks}
        return [by_id[i].model_dump(mode="json") for i in ids]

    def run(self, task, config, prompt):
        from openai import APIError
        from tau2.data_model.message import UserMessage
        from tau2.data_model.tasks import Task
        from tau2.evaluator.evaluator import EvaluationType
        from tau2.orchestrator.orchestrator import Orchestrator
        from tau2.runner import build_environment, run_simulation
        from tau2.user.user_simulator_base import STOP, HalfDuplexUser, UserError

        task = Task.model_validate(task)
        criteria = task.evaluation_criteria
        if criteria and (criteria.nl_assertions or "COMMUNICATE" in criteria.reward_basis):
            raise ValueError(
                "Mock refuses tasks requiring an LLM Judge; official scoring unchanged"
            )

        class ScriptedUser(HalfDuplexUser):
            def set_seed(self, seed):
                self.seed = seed  # No RNG: this participant is a fixed script.

            def get_init_state(self, message_history=None):
                return list(message_history or [])

            def generate_next_message(self, message, state):
                first_turn = not any(isinstance(m, UserMessage) for m in state)
                if message is not None:
                    state.append(message)
                response = UserMessage(
                    role="user", content=("Inspect my order." if first_turn else STOP)
                )
                state.append(response)
                return response, state

        # Fresh official environment and fresh participants on every call, even repeated task IDs.
        environment = build_environment("retail")
        if environment.get_policy() != prompt.policy:
            raise ValueError("Official Policy changed during run")
        agent = make_agent(
            prompt,
            environment.get_tools(),
            config.agent_model,
            config.agent_args or {},
            scripted=True,
        )
        orchestrator = Orchestrator(
            domain="retail",
            agent=agent,
            user=ScriptedUser(),
            environment=environment,
            task=task,
            max_steps=config.max_steps,
            max_errors=2,
            seed=config.seed,
        )
        try:
            result = run_simulation(orchestrator, evaluation_type=EvaluationType.ALL)
        except APIError:
            raise ProviderError("Provider failure; details withheld") from None
        except UserError:
            raise SimulatorError("User simulator failure; details withheld") from None
        # Preserve the original upstream result. Project seed/trial/mode live in sidecars.
        return result.model_dump(mode="json")
