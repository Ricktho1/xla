import os
import unittest
from typing import Callable, Dict, List

import torch
import torch_xla.core.xla_model as xm
from torch._higher_order_ops.while_loop import while_loop

_TORCH_WHILE_LOOP_OPS = [
    torch._higher_order_ops.while_loop,
]

def _fake_while_loop(cond_fn, body_fn, operands):
    while cond_fn(*operands):
        operands = body_fn(*operands)
    return operands

def _while_loop_tests():
    def simple(x):
        def cond_fn(x):
            return x.sum() < 10

        def body_fn(x):
            return (x + 1,)

        return while_loop(cond_fn, body_fn, (x, ))

    def simple_with_mutation(x):
        def cond_fn(x):
            y = x.clone().add_(1).add_(-1)
            return y.sum() < 10

        def body_fn(x):
            y = x.clone().add_(1).add_(-1)
            return (y + 1,)

        return while_loop(cond_fn, body_fn, (x, ))

    def nested(out_iter, it, y):
        def cond_fn(out_iter, it, y):
            return it.sum() < 10

        def body_fn(out_iter, it, y):
            return (out_iter.clone(), it + y, y + 1)

        def outer_cond_fn(out_iter, it, y):
            return out_iter.sum() < 2

        def outer_body_fn(out_iter, it, y):
            out_iter, it, y = while_loop(cond_fn, body_fn, (out_iter, it, y))
            return (out_iter + 1, it, y)

        return while_loop(outer_cond_fn, outer_body_fn, (out_iter, it, y))


    x = torch.zeros(1)
    y = torch.zeros(1)
    z = torch.zeros(1)
    return {"simple": (simple, (x,)),
            "nested": (nested, (x, y, z)),
            "simple_with_mutation": (simple_with_mutation, (x,))}

class WhileLoopTest(unittest.TestCase):

    def test_while_loop_tpu(self):
        def cond_fn(x):
            return x.sum() < 10

        def body_fn(x):
            return (x + 1,)

        device = xm.xla_device()
        x = torch.zeros(1, device=device)
        res = while_loop(cond_fn, body_fn, (x, ))
        expected = _fake_while_loop(cond_fn, body_fn, (x, ))
        self.assertEqual(expected, res)



if __name__ == '__main__':
  test = unittest.main()
  sys.exit(0 if test.result.wasSuccessful() else 1)
