import unittest
from enum import Enum

from metaflow.flowspec import _FlowState


class _Key(Enum):
    A = 1
    B = 2


class TestFlowStateCacheInvalidation(unittest.TestCase):
    def _make_state(self, initial_self, inherited=None):
        state = _FlowState(initial_self)
        if inherited:
            state._inherited.update(inherited)
        return state

    def test_setitem_override_replaces_decorator(self):
        state = self._make_state({_Key.A: {"project": ["old"]}, _Key.B: None})
        state._inherited[_Key.A] = {}

        flow_decos = state[_Key.A]
        self.assertEqual(flow_decos["project"], ["old"])

        state[_Key.A] = {k: v for k, v in flow_decos.items() if k != "project"}

        flow_decos = state[_Key.A]
        flow_decos.setdefault("project", []).append("new")

        result = state[_Key.A]
        self.assertEqual(len(result["project"]), 1)
        self.assertEqual(result["project"][0], "new")

    def test_write_without_prior_read(self):
        state = self._make_state({_Key.A: {"x": [1]}, _Key.B: None})
        state[_Key.A] = {"y": [2]}
        self.assertEqual(state[_Key.A], {"y": [2]})

    def test_consecutive_overrides(self):
        state = self._make_state({_Key.A: {"x": [1]}, _Key.B: None})
        state._inherited[_Key.A] = {}

        state[_Key.A] = {"y": [2]}
        self.assertIn("y", state[_Key.A])
        self.assertNotIn("x", state[_Key.A])

        state[_Key.A] = {"z": [3]}
        self.assertIn("z", state[_Key.A])
        self.assertNotIn("y", state[_Key.A])


if __name__ == "__main__":
    unittest.main()
