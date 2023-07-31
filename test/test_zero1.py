import torch
import torch.nn as nn
import torch_xla
import torch_xla.core.xla_model as xm
from torch_xla.distributed.zero_redundancy_optimizer import ZeroRedundancyOptimizer
from torch_xla import runtime as xr
from torch.testing._internal.common_utils import TestCase
from copy import deepcopy

import unittest


class XlaZeRO1Test(TestCase):

  @unittest.skipIf(xr.device_type() == 'TPU', "Crash on TPU")
  @unittest.skipIf(xr.device_type() == 'GPU',
                   "TODO(alanwaketan): Fix it for the token change.")
  def test_zero1(self):
    device = xm.xla_device()

    model = nn.Linear(8, 8)
    x = torch.ones((8, 8))
    model = model.to(device)
    x = x.to(device)
    y = model(x).sum()
    y.backward()

    opt1 = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    opt2 = ZeroRedundancyOptimizer(
        model.parameters(),
        torch.optim.SGD,
        lr=0.01,
        momentum=0.9,
        grad_clipping=False)

    opt1.step()
    opt2.step()
    s1 = opt1.state_dict()
    s2 = opt2.state_dict()
    print("AFTER STEPPING ONCE")
    print("opt1.state", opt1.state)
    print("opt1.state_dict()", s1)
    print("opt2.state[base]", opt2.state['base'])
    print("opt2.state_dict()[base]", s2['base'])
    self.assertEqual(s1, s2['base'])

    # s1_clone = deepcopy(s1)
    # s2_clone = deepcopy(s2)
    opt1.load_state_dict(s1)
    opt2.load_state_dict(s2)
    print("AFTER LOADING THE STATE_DICTs, should be same as before")
    print("opt1.state", opt1.state)
    print("opt1.state_dict()", opt1.state_dict())
    print("opt2.state", opt2.state['base'])
    print("opt2.state_dict()[base]", opt2.state_dict()['base'])
    self.assertEqual(opt1.state_dict(), opt2.state_dict()['base'])

    # step still runnable
    opt1.step()
    opt2.step()
    print("AFTER STEPPING AGAIN, WILL be different")
    print("opt1.state", opt1.state)
    print("opt1.state_dict()", opt1.state_dict())
    print("opt2.state", opt2.state['base'])
    print("opt2.state_dict()[base]", opt2.state_dict()['base'])
    opt1.load_state_dict(s1)
    opt2.load_state_dict(s2)
    print("AFTER LOADING THE STATE_DICTs, should be same as before")
    print("opt1.state", opt1.state)
    print("opt1.state_dict()", opt1.state_dict())
    print("opt2.state", opt2.state['base'])
    print("opt2.state_dict()[base]", opt2.state_dict()['base'])
    self.assertEqual(opt1.state_dict(), opt2.state_dict()['base'])

    # step still runnable
    opt1.step()
    opt2.step()


if __name__ == '__main__':
  test = unittest.main()
  sys.exit(0 if test.result.wasSuccessful() else 1)
