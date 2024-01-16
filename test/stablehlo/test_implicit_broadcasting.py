# import re
# import sys
# import unittest

# import torch
# import torch_xla
# from torch_xla.core import xla_model as xm
# from typing import Tuple, Type, Callable, Union, List

# # The following tests cover the implcit-broadcasting for static and bounded
# # dynamic shapes.

# device = xm.xla_device()


# class ImplicitBroadcasting(unittest.TestCase):

#   ## broadcasting with static shapes
#   def test_same_rank_broadcast_with_static_shapes(self):
#     a = torch.randn((10, 1)).to(device=device)
#     b = torch.randn((1, 5)).to(device=device)
#     c = a * b
#     stablehlo_text = xm.get_stablehlo([c])
#     self.assertTrue(
#         re.search(r'stablehlo.multiply.* : tensor<10x5xf32>', stablehlo_text)
#         is not None)

#   def test_scalar_broadcast_with_static_shapes(self):
#     a = torch.randn(()).to(device=device)
#     b = torch.randn((1, 5)).to(device=device)
#     c = a * b
#     stablehlo_text = xm.get_stablehlo([c])
#     self.assertTrue(
#         re.search(r'stablehlo.multiply.* : tensor<1x5xf32>', stablehlo_text)
#         is not None)

#   def test_different_rank_broadcast_with_static_shapes(self):
#     a = torch.randn((10, 1)).to(device=device)
#     b = torch.randn((6, 8, 1, 5)).to(device=device)
#     c = a * b
#     stablehlo_text = xm.get_stablehlo([c])
#     self.assertTrue(
#         re.search(r'stablehlo.multiply.* : tensor<6x8x10x5xf32>',
#                   stablehlo_text) is not None)

<<<<<<< HEAD
#   ## broadcasting with unbounded dynamic shapes
# <<<<<<< HEAD
#   ### (10,?) * c
# =======
#   ### (X,?) * c
# >>>>>>> 6961241db (unbounded implelcit broadcasting)
#   def test_scalar_broadcast_with_unbounded_dynamic_shapes(self):
#     a = torch.randn(()).to(device=device)
#     b = torch.randn((10, 5)).to(device=device)
#     torch_xla._XLAC._xla_mark_dynamic(b, 1)
#     c = a * b
#     stablehlo_text = xm.get_stablehlo([c])
#     self.assertTrue(
#         re.search(
#             r'dynamic_broadcast_in_dim.*=.*\[\].*: \(tensor<f32>, tensor<2xi32>\) -> tensor<10x\?xf32>',
#             stablehlo_text) is not None)
#     self.assertTrue(
#         re.search(
#             r'dynamic_broadcast_in_dim.*=.*\[0, 1\].*: \(tensor<10x\?xf32>, tensor<2xi32>\) -> tensor<10x\?xf32>',
#             stablehlo_text) is not None)

# <<<<<<< HEAD
#   ### (?) * (10)
# =======
#   ### (?) * (X)
# >>>>>>> 6961241db (unbounded implelcit broadcasting)
#   def test_same_rank_broadcast_with_unbounded_dynamic_shapes_1(self):
#     a = torch.randn((10)).to(device=device)
#     b = torch.randn((10)).to(device=device)
#     torch_xla._XLAC._xla_mark_dynamic(a, 0)
#     c = a * b
#     stablehlo_text = xm.get_stablehlo([c])
#     self.assertTrue(
#         re.search(
# <<<<<<< HEAD
#             r'dynamic_broadcast_in_dim.*=.*\[0\].*: \(tensor<\?xf32>, tensor<1xi32>\) -> tensor<10xf32>',
#             stablehlo_text) is not None)
# <<<<<<< HEAD
# =======
#     self.assertTrue(
#         re.search(
#             r'dynamic_broadcast_in_dim.*=.*\[0\].*: \(tensor<10xf32>, tensor<1xi32>\) -> tensor<10xf32>',
# =======
#             r'dynamic_broadcast_in_dim.*=.*\[0\].*: \(tensor<\?xf32>, tensor<1xi32>\) -> tensor<\?xf32>',
#             stablehlo_text) is not None)
#     self.assertTrue(
#         re.search(
#             r'dynamic_broadcast_in_dim.*=.*\[0\].*: \(tensor<10xf32>, tensor<1xi32>\) -> tensor<\?xf32>',
# >>>>>>> 6961241db (unbounded implelcit broadcasting)
#             stablehlo_text) is not None)
# >>>>>>> 02cbe918c (fix rebase)
=======
  ## broadcasting with unbounded dynamic shapes
  def test_scalar_broadcast_with_unbounded_dynamic_shapes(self):
    a = torch.randn(()).to(device=device)
    b = torch.randn((10, 5)).to(device=device)
    torch_xla._XLAC._xla_mark_dynamic(b, 1)
    c = a * b
    stablehlo_text = xm.get_stablehlo([c])
    self.assertTrue(
        re.search(
            r'dynamic_broadcast_in_dim.*=.*\[\].*: \(tensor<f32>, tensor<2xi32>\) -> tensor<10x\?xf32>',
            stablehlo_text) is not None)
    self.assertTrue(
        re.search(
            r'dynamic_broadcast_in_dim.*=.*\[0, 1\].*: \(tensor<10x\?xf32>, tensor<2xi32>\) -> tensor<10x\?xf32>',
            stablehlo_text) is not None)


  def test_same_rank_broadcast_with_unbounded_dynamic_shapes_1(self):
    a = torch.randn((10)).to(device=device)
    b = torch.randn((10)).to(device=device)
    torch_xla._XLAC._xla_mark_dynamic(a, 0)
    c = a * b
    stablehlo_text = xm.get_stablehlo([c])
    # print(stablehlo_text)
    self.assertTrue(
        re.search(
            r'dynamic_broadcast_in_dim.*=.*\[0\].*: \(tensor<\?xf32>, tensor<1xi32>\) -> tensor<\?xf32>',
            stablehlo_text) is not None)
    self.assertTrue(
        re.search(
            r'dynamic_broadcast_in_dim.*=.*\[0\].*: \(tensor<10xf32>, tensor<1xi32>\) -> tensor<\?xf32>',
<<<<<<< HEAD
>>>>>>> 6961241db (unbounded implelcit broadcasting)
=======
            r'dynamic_broadcast_in_dim.*=.*\[0\].*: \(tensor<\?xf32>, tensor<1xi32>\) -> tensor<10xf32>',
            stablehlo_text) is not None)
    self.assertTrue(
        re.search(
            r'dynamic_broadcast_in_dim.*=.*\[0\].*: \(tensor<10xf32>, tensor<1xi32>\) -> tensor<10xf32>',
>>>>>>> 249b8b3c1 (Address feedback:II)
            stablehlo_text) is not None)
>>>>>>> 88ad63edb (fix rebase)
=======
>>>>>>> c9359372e (e2e prototype for hf_vit_base_patch16_224)

<<<<<<< HEAD
#   ### (?,?) * (?,1)
#   def test_same_rank_broadcast_with_unbounded_dynamic_shapes_2(self):
#     a = torch.randn((5, 10)).to(device=device)
#     b = torch.randn((5, 1)).to(device=device)
#     torch_xla._XLAC._xla_mark_dynamic(a, 0)
#     torch_xla._XLAC._xla_mark_dynamic(a, 1)
#     torch_xla._XLAC._xla_mark_dynamic(b, 0)
#     c = a * b
#     stablehlo_text = xm.get_stablehlo([c])
#     self.assertTrue(
#         re.search(
#             r'dynamic_broadcast_in_dim.*=.*\[0, 1\].*: \(tensor<\?x\?xf32>, tensor<2xi32>\) -> tensor<\?x\?xf32>',
#             stablehlo_text) is not None)
#     self.assertTrue(
#         re.search(
#             r'dynamic_broadcast_in_dim.*=.*\[0, 1\].*: \(tensor<\?x1xf32>, tensor<2xi32>\) -> tensor<\?x\?xf32>',
#             stablehlo_text) is not None)
=======
  ### (?,?) * (?,1)
  def test_same_rank_broadcast_with_unbounded_dynamic_shapes_2(self):
    a = torch.randn((5, 10)).to(device=device)
    b = torch.randn((5, 1)).to(device=device)
    torch_xla._XLAC._xla_mark_dynamic(a, 0)
    torch_xla._XLAC._xla_mark_dynamic(a, 1)
    torch_xla._XLAC._xla_mark_dynamic(b, 0)
    c = a * b
    stablehlo_text = xm.get_stablehlo([c])
    print(stablehlo_text)
    self.assertTrue(
        re.search(
            r'dynamic_broadcast_in_dim.*=.*\[0, 1\].*: \(tensor<\?x\?xf32>, tensor<2xi32>\) -> tensor<\?x\?xf32>',
            stablehlo_text) is not None)
    self.assertTrue(
        re.search(
            r'dynamic_broadcast_in_dim.*=.*\[0, 1\].*: \(tensor<\?x1xf32>, tensor<2xi32>\) -> tensor<\?x\?xf32>',
            stablehlo_text) is not None)
>>>>>>> df36582a5 (add dynamic expand)

#   ### (?,?) * (?,?)
#   def test_same_rank_broadcast_with_unbounded_dynamic_shapes_3(self):
#     a = torch.randn((10, 5)).to(device=device)
#     b = torch.randn((10, 5)).to(device=device)
#     torch_xla._XLAC._xla_mark_dynamic(a, 0)
#     torch_xla._XLAC._xla_mark_dynamic(a, 1)
#     torch_xla._XLAC._xla_mark_dynamic(b, 0)
#     torch_xla._XLAC._xla_mark_dynamic(b, 1)
#     c = a * b
#     stablehlo_text = xm.get_stablehlo([c])
#     self.assertTrue(
#         re.search(
#             r'dynamic_broadcast_in_dim.*=.*\[0, 1\].*: \(tensor<\?x\?xf32>, tensor<2xi32>\) -> tensor<\?x\?xf32>',
#             stablehlo_text) is not None)
#     self.assertTrue(
#         re.search(
#             r'dynamic_broadcast_in_dim.*=.*\[0, 1\].*: \(tensor<\?x\?xf32>, tensor<2xi32>\) -> tensor<\?x\?xf32>',
#             stablehlo_text) is not None)

#   ### (?,5) * (?,1)
#   def test_same_rank_broadcast_with_unbounded_dynamic_shapes_4(self):
#     a = torch.randn((5, 5)).to(device=device)
#     b = torch.randn((5, 1)).to(device=device)
#     torch_xla._XLAC._xla_mark_dynamic(a, 0)
#     torch_xla._XLAC._xla_mark_dynamic(b, 0)
#     c = a * b
#     stablehlo_text = xm.get_stablehlo([c])
#     self.assertTrue(
#         re.search(
#             r'dynamic_broadcast_in_dim.*=.*\[0, 1\].*: \(tensor<\?x1xf32>, tensor<2xi32>\) -> tensor<\?x5xf32>',
#             stablehlo_text) is not None)
#     self.assertTrue(
#         re.search(
#             r'dynamic_broadcast_in_dim.*=.*\[0, 1\].*: \(tensor<\?x5xf32>, tensor<2xi32>\) -> tensor<\?x5xf32>',
#             stablehlo_text) is not None)

<<<<<<< HEAD
<<<<<<< HEAD
# <<<<<<< HEAD
#   ### (?,5,?) * (1,?)
# =======
#   ### (?,X,?)) * (1,?)
# >>>>>>> 6961241db (unbounded implelcit broadcasting)
#   def test_different_rank_broadcast_with_unbounded_dynamic_shapes_1(self):
#     a = torch.randn((10, 5, 4)).to(device=device)
#     b = torch.randn((1, 4)).to(device=device)
#     torch_xla._XLAC._xla_mark_dynamic(a, 0)
#     torch_xla._XLAC._xla_mark_dynamic(a, 2)
#     torch_xla._XLAC._xla_mark_dynamic(b, 1)
#     c = a * b
#     stablehlo_text = xm.get_stablehlo([c])
#     self.assertTrue(
#         re.search(
#             r'dynamic_broadcast_in_dim.*=.*\[1, 2\].*: \(tensor<1x\?xf32>, tensor<3xi32>\) -> tensor<\?x5x\?xf32>',
#             stablehlo_text) is not None)
#     self.assertTrue(
#         re.search(
#             r'dynamic_broadcast_in_dim.*=.*\[0, 1, 2\].*: \(tensor<\?x5x\?xf32>, tensor<3xi32>\) -> tensor<\?x5x\?xf32>',
#             stablehlo_text) is not None)

# <<<<<<< HEAD
#   ### (?,?,?) * (?,?)
# =======
#   ### (?,?,?)) * (?,?)
# >>>>>>> 6961241db (unbounded implelcit broadcasting)
#   def test_different_rank_broadcast_with_unbounded_dynamic_shapes_2(self):
#     a = torch.randn((10, 5, 4)).to(device=device)
#     b = torch.randn((1, 4)).to(device=device)
#     torch_xla._XLAC._xla_mark_dynamic(a, 0)
#     torch_xla._XLAC._xla_mark_dynamic(a, 1)
#     torch_xla._XLAC._xla_mark_dynamic(a, 2)
#     torch_xla._XLAC._xla_mark_dynamic(b, 0)
#     torch_xla._XLAC._xla_mark_dynamic(b, 1)
#     c = a * b
#     stablehlo_text = xm.get_stablehlo([c])
#     self.assertTrue(
#         re.search(
#             r'dynamic_broadcast_in_dim.*=.*\[1, 2\].*: \(tensor<\?x\?xf32>, tensor<3xi32>\) -> tensor<\?x\?x\?xf32>',
#             stablehlo_text) is not None)
#     self.assertTrue(
#         re.search(
#             r'dynamic_broadcast_in_dim.*=.*\[0, 1, 2\].*: \(tensor<\?x\?x\?xf32>, tensor<3xi32>\) -> tensor<\?x\?x\?xf32>',
#             stablehlo_text) is not None)
=======
<<<<<<< HEAD
<<<<<<< HEAD
  ### (?,5,?) * (1,?)
=======
  ### (?,X,?)) * (1,?)
>>>>>>> 6961241db (unbounded implelcit broadcasting)
=======
  ### (?,5,?) * (1,?)
>>>>>>> 659bd534d (Address feedback:I)
=======
>>>>>>> c9359372e (e2e prototype for hf_vit_base_patch16_224)
  def test_different_rank_broadcast_with_unbounded_dynamic_shapes_1(self):
    a = torch.randn((10, 5, 4)).to(device=device)
    b = torch.randn((1, 4)).to(device=device)
    torch_xla._XLAC._xla_mark_dynamic(a, 0)
    torch_xla._XLAC._xla_mark_dynamic(a, 2)
    torch_xla._XLAC._xla_mark_dynamic(b, 1)
    c = a * b
    stablehlo_text = xm.get_stablehlo([c])
    self.assertTrue(
        re.search(
            r'dynamic_broadcast_in_dim.*=.*\[1, 2\].*: \(tensor<1x\?xf32>, tensor<3xi32>\) -> tensor<\?x5x\?xf32>',
            stablehlo_text) is not None)
    self.assertTrue(
        re.search(
            r'dynamic_broadcast_in_dim.*=.*\[0, 1, 2\].*: \(tensor<\?x5x\?xf32>, tensor<3xi32>\) -> tensor<\?x5x\?xf32>',
            stablehlo_text) is not None)

  def test_different_rank_broadcast_with_unbounded_dynamic_shapes_2(self):
    a = torch.randn((10, 5, 4)).to(device=device)
    b = torch.randn((1, 4)).to(device=device)
    torch_xla._XLAC._xla_mark_dynamic(a, 0)
    torch_xla._XLAC._xla_mark_dynamic(a, 1)
    torch_xla._XLAC._xla_mark_dynamic(a, 2)
    torch_xla._XLAC._xla_mark_dynamic(b, 0)
    torch_xla._XLAC._xla_mark_dynamic(b, 1)
    c = a * b
    stablehlo_text = xm.get_stablehlo([c])
    self.assertTrue(
        re.search(
            r'dynamic_broadcast_in_dim.*=.*\[1, 2\].*: \(tensor<\?x\?xf32>, tensor<3xi32>\) -> tensor<\?x\?x\?xf32>',
            stablehlo_text) is not None)
    self.assertTrue(
        re.search(
            r'dynamic_broadcast_in_dim.*=.*\[0, 1, 2\].*: \(tensor<\?x\?x\?xf32>, tensor<3xi32>\) -> tensor<\?x\?x\?xf32>',
            stablehlo_text) is not None)
>>>>>>> 88ad63edb (fix rebase)

<<<<<<< HEAD
<<<<<<< HEAD
# <<<<<<< HEAD
#   ### (2,5) * (?)
#   def test_different_rank_broadcast_with_unbounded_dynamic_shapes_3(self):
#     a = torch.randn((2, 5)).to(device=device)
#     b = torch.randn((5)).to(device=device)
#     torch_xla._XLAC._xla_mark_dynamic(b, 0)
#     c = a * b
#     stablehlo_text = xm.get_stablehlo([c])
#     self.assertTrue(
#         re.search(
#             r'dynamic_broadcast_in_dim.*=.*\[1\].*: \(tensor<\?xf32>, tensor<2xi32>\) -> tensor<2x5xf32>',
#             stablehlo_text) is not None)

# =======
# >>>>>>> 6961241db (unbounded implelcit broadcasting)
=======
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 249b8b3c1 (Address feedback:II)
=======
>>>>>>> c9359372e (e2e prototype for hf_vit_base_patch16_224)
  ### (2,5) * (?)
  def test_different_rank_broadcast_with_unbounded_dynamic_shapes_3(self):
    a = torch.randn((2, 5)).to(device=device)
    b = torch.randn((5)).to(device=device)
    torch_xla._XLAC._xla_mark_dynamic(b, 0)
    c = a * b
    stablehlo_text = xm.get_stablehlo([c])
    self.assertTrue(
        re.search(
            r'dynamic_broadcast_in_dim.*=.*\[1\].*: \(tensor<\?xf32>, tensor<2xi32>\) -> tensor<2x5xf32>',
            stablehlo_text) is not None)

<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 6961241db (unbounded implelcit broadcasting)
=======
>>>>>>> 249b8b3c1 (Address feedback:II)
>>>>>>> 0f3f34019 (fix rebase)

# if __name__ == '__main__':
#   test = unittest.main()
#   sys.exit(0 if test.result.wasSuccessful() else 1)
=======
if __name__ == '__main__':
  test = unittest.main()
  sys.exit(0 if test.result.wasSuccessful() else 1)
>>>>>>> c9359372e (e2e prototype for hf_vit_base_patch16_224)
