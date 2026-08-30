"""Test bootstrap.

balatro_env/__init__ imports env.py, which imports torch at module scope (and uses torch.Tensor
in annotations). torch is heavy and not installed on every dev machine, so when it is missing
we register a minimal stand-in whose attributes are inert placeholders. The offline tests never
touch tensor code; anything that does must skip without real torch.
"""

import sys
import types

try:
    import torch  # noqa: F401
except ModuleNotFoundError:
    class _TorchStub(types.ModuleType):
        __stub__ = True

        def __getattr__(self, name):
            return object

    sys.modules["torch"] = _TorchStub("torch")
