#include "tensor_util.h"

#include <algorithm>
#include <functional>
#include <list>
#include <numeric>

#include "helpers.h"
#include "tensorflow/compiler/xla/literal_util.h"
#include "tensorflow/compiler/xla/shape_util.h"
#include "tensorflow/compiler/xla/xla_client/debug_macros.h"
#include "tensorflow/core/lib/bfloat16/bfloat16.h"

namespace torch_xla {
namespace {

// Creates a minor-to-major layout from given dimensions.
xla::Shape MakeTorchTensorLayout(const std::vector<xla::int64>& dimensions,
                                 xla::PrimitiveType type) {
  return xla::ShapeUtil::MakeShapeWithDescendingLayout(type, dimensions);
}

xla::PrimitiveType GetTorchDataType(xla::PrimitiveType type) {
  return type == xla::PrimitiveType::BF16 ? xla::PrimitiveType::F32 : type;
}

// Copies n bytes from source to dest, with different stride values for source
// and destination.
template <typename S, typename D>
void StridedCopy(D* dest, xla::int64 dest_stride, const S* source,
                 xla::int64 source_stride, xla::int64 n) {
  for (; n > 0; --n, dest += dest_stride, source += source_stride) {
    *dest = static_cast<D>(*source);
  }
}

// Computes the offset of the value at a given index, assuming a contiguous/flat
// tensor data representation.
template <typename S>
xla::int64 GetFlatTensorOffset(const S& strides,
                               const std::vector<xla::int64>& indices) {
  xla::int64 base = 0;
  for (size_t i = 0; i < indices.size(); ++i) {
    base += indices[i] * strides[i];
  }
  return base;
}

std::vector<xla::int64> ComputeShapeStrides(const xla::Shape& shape) {
  std::vector<xla::int64> strides(shape.rank());
  xla::int64 stride = 1;
  for (auto dim : shape.layout().minor_to_major()) {
    strides[dim] = stride;
    stride *= shape.dimensions(dim);
  }
  return strides;
}

template <typename D, typename S>
void CopyData(D* dest, const S* source, xla::int64 n) {
  StridedCopy(dest, 1, source, 1, n);
}

template <>
void CopyData<float, float>(float* dest, const float* source, xla::int64 n) {
  std::copy(source, source + n, dest);
}

template <>
void CopyData<xla::int64, int64_t>(xla::int64* dest, const int64_t* source,
                                   xla::int64 n) {
  std::copy(source, source + n, dest);
}

std::vector<xla::int64> GetIterationDimensions(const xla::Shape& shape) {
  // Return the most minor dimension order, to iterate the literal memory in a
  // cache friendly way.
  // Another strategy could be to return the higher value dimension first, to
  // reduce the number of outer loops in TensorToBuffer(), but that leads to
  // StridedCopy() calls in which both source and destination are jumping off
  // memory locations.
  return std::vector<xla::int64>(shape.layout().minor_to_major().begin(),
                                 shape.layout().minor_to_major().end());
}

template <typename SType, typename DType>
void CopyTensors(const void* src_buffer, const xla::Shape& src_shape,
                 void* dest_buffer, size_t dest_buffer_size,
                 const xla::Shape& dest_shape) {
  XLA_CHECK(
      xla::ShapeUtil::CompatibleIgnoringElementType(src_shape, dest_shape))
      << src_shape << " vs. " << dest_shape;

  xla::int64 total_elements = xla::ShapeUtil::ElementsIn(src_shape);
  XLA_CHECK_EQ(dest_buffer_size, total_elements * sizeof(DType));

  const SType* src_data = reinterpret_cast<const SType*>(src_buffer);
  DType* dest_data = reinterpret_cast<DType*>(dest_buffer);
  if (xla::ShapeUtil::EqualIgnoringFpPrecision(src_shape, dest_shape)) {
    CopyData<DType, SType>(dest_data, src_data, total_elements);
  } else {
    std::vector<xla::int64> src_strides = ComputeShapeStrides(src_shape);
    std::vector<xla::int64> dest_strides = ComputeShapeStrides(dest_shape);
    std::vector<xla::int64> indices(src_strides.size());
    std::vector<xla::int64> iter_dims = GetIterationDimensions(dest_shape);
    xla::int64 inner_src_stride = src_strides[iter_dims.front()];
    xla::int64 inner_dest_stride = dest_strides[iter_dims.front()];
    xla::int64 n = 0;
    while (n < iter_dims.size()) {
      StridedCopy(dest_data + GetFlatTensorOffset(dest_strides, indices),
                  inner_dest_stride,
                  src_data + GetFlatTensorOffset(src_strides, indices),
                  inner_src_stride, dest_shape.dimensions(iter_dims.front()));
      // Compute the next index. Skip the lower iteration dimension, as we loop
      // over it using the StridedCopy() call above.
      for (n = 1; n < iter_dims.size(); ++n) {
        xla::int64 dim = iter_dims[n];
        indices[dim] += 1;
        if (indices[dim] < dest_shape.dimensions(dim)) {
          break;
        }
        indices[dim] = 0;
      }
    }
  }
}

template <typename SType, typename DType>
void TensorToBuffer(const at::Tensor& tensor, const xla::Shape& shape,
                    void* dest_buffer, size_t dest_buffer_size) {
  at::Tensor contiguous_tensor = tensor.contiguous();
  xla::Shape src_shape = MakeTorchTensorLayout(
      XlaHelpers::I64List(contiguous_tensor.sizes()),
      XlaHelpers::MakeXlaPrimitiveType(contiguous_tensor.type().scalarType()));
  CopyTensors<SType, DType>(contiguous_tensor.data<SType>(), src_shape,
                            dest_buffer, dest_buffer_size, shape);
}

void PopulateTensorBuffer(const at::Tensor& tensor, const xla::Shape& shape,
                          void* dest_buffer, size_t dest_buffer_size) {
  switch (tensor.type().scalarType()) {
    case at::ScalarType::Float:
      if (shape.element_type() == xla::PrimitiveType::BF16) {
        TensorToBuffer<float, tensorflow::bfloat16>(tensor, shape, dest_buffer,
                                                    dest_buffer_size);
      } else {
        TensorToBuffer<float, float>(tensor, shape, dest_buffer,
                                     dest_buffer_size);
      }
      break;
    case at::ScalarType::Byte:
      TensorToBuffer<uint8_t, xla::uint8>(tensor, shape, dest_buffer,
                                          dest_buffer_size);
      break;
    case at::ScalarType::Char:
      TensorToBuffer<int8_t, xla::int8>(tensor, shape, dest_buffer,
                                        dest_buffer_size);
      break;
    case at::ScalarType::Short:
      TensorToBuffer<int16_t, xla::int16>(tensor, shape, dest_buffer,
                                          dest_buffer_size);
      break;
    case at::ScalarType::Int:
      TensorToBuffer<int32_t, xla::int32>(tensor, shape, dest_buffer,
                                          dest_buffer_size);
      break;
    case at::ScalarType::Long:
      TensorToBuffer<int64_t, xla::int64>(tensor, shape, dest_buffer,
                                          dest_buffer_size);
      break;
    default:
      XLA_ERROR() << "Tensor type not supported: " << tensor.type();
  }
}

std::shared_ptr<xla::ComputationClient::Data> TensorToXlaData(
    const at::Tensor& tensor, const xla::Shape& shape, const Device& device) {
  auto populate_fn =
      [&](const xla::ComputationClient::TensorSource& source_tensor,
          void* dest_buffer, size_t dest_buffer_size) {
        PopulateTensorBuffer(tensor, source_tensor.shape, dest_buffer,
                             dest_buffer_size);
      };

  std::vector<xla::ComputationClient::TensorSource> source_tensors;
  source_tensors.emplace_back(shape, device.ToString(), std::move(populate_fn));

  auto handles =
      xla::ComputationClient::Get()->TransferToServer(source_tensors);
  XLA_CHECK_EQ(handles.size(), 1);
  return std::move(handles.front());
}

at::ScalarType TensorTypeFromXlaType(xla::PrimitiveType type) {
  switch (type) {
    case xla::PrimitiveType::BF16:
    case xla::PrimitiveType::F32:
      return at::ScalarType::Float;
    case xla::PrimitiveType::U8:
      return at::ScalarType::Byte;
    case xla::PrimitiveType::S8:
      return at::ScalarType::Char;
    case xla::PrimitiveType::S16:
      return at::ScalarType::Short;
    case xla::PrimitiveType::S32:
      return at::ScalarType::Int;
    case xla::PrimitiveType::S64:
      return at::ScalarType::Long;
    default:
      XLA_ERROR() << "Unknown XLA primitive type: " << type;
  }
}

template <typename SType, typename DType>
at::Tensor XlaLiteralToTensor(const xla::Literal& literal) {
  std::vector<int64_t> dimensions;
  for (auto result_dimension : literal.shape().dimensions()) {
    dimensions.push_back(result_dimension);
  }
  xla::Shape torch_shape =
      MakeTorchTensorLayout(literal.shape().dimensions(),
                            GetTorchDataType(literal.shape().element_type()));
  xla::int64 total_elements = xla::ShapeUtil::ElementsIn(torch_shape);

  const auto literal_data = literal.data<SType>();
  at::Tensor tensor = at::empty(
      dimensions,
      at::TensorOptions(TensorTypeFromXlaType(literal.shape().element_type())));
  CopyTensors<SType, DType>(literal_data.data(), literal.shape(),
                            tensor.data<DType>(),
                            total_elements * sizeof(DType), torch_shape);
  return tensor;
}

}  // namespace

at::Tensor MakeTensorFromXlaLiteral(const xla::Literal& literal) {
  switch (literal.shape().element_type()) {
    case xla::PrimitiveType::BF16: {
      return XlaLiteralToTensor<tensorflow::bfloat16, float>(literal);
    }
    case xla::PrimitiveType::F32: {
      return XlaLiteralToTensor<float, float>(literal);
    }
    case xla::PrimitiveType::U8: {
      return XlaLiteralToTensor<xla::uint8, uint8_t>(literal);
    }
    case xla::PrimitiveType::S8: {
      return XlaLiteralToTensor<xla::int8, int8_t>(literal);
    }
    case xla::PrimitiveType::S16: {
      return XlaLiteralToTensor<xla::int16, int16_t>(literal);
    }
    case xla::PrimitiveType::S32: {
      return XlaLiteralToTensor<xla::int32, int32_t>(literal);
    }
    case xla::PrimitiveType::S64: {
      return XlaLiteralToTensor<xla::int64, int64_t>(literal);
    }
    default:
      XLA_ERROR() << "Unsupported literal type: " << literal.shape();
  }
}

xla::Shape MakeArrayShapeFromDimensions(const at::IntList& tensor_dimensions,
                                        xla::PrimitiveType type,
                                        DeviceType device_type) {
  const auto dimensions = XlaHelpers::I64List(tensor_dimensions);
  if (dimensions.size() == 4 && device_type == DeviceType::TPU) {
    // Use a TPU-compatible layout for 4D tensors -- batch and feature in minor
    // dimensions (HWCN).
    return xla::ShapeUtil::MakeShapeWithLayout(type, dimensions, {0, 1, 3, 2});
  }
  return MakeTorchTensorLayout(dimensions, type);
}

std::shared_ptr<xla::ComputationClient::Data> TensorToXlaData(
    const at::Tensor& tensor, const Device& device) {
  return TensorToXlaData(
      tensor,
      MakeArrayShapeFromDimensions(
          tensor.sizes(),
          XlaHelpers::MakeXlaPrimitiveType(tensor.type().scalarType()),
          device.hw_type),
      device);
}

std::vector<std::shared_ptr<xla::ComputationClient::Data>> CreateTensorsData(
    const std::vector<at::Tensor>& tensors,
    const std::vector<std::string>& devices) {
  XLA_CHECK_EQ(tensors.size(), devices.size());
  std::vector<xla::ComputationClient::TensorSource> source_tensors;
  for (size_t i = 0; i < tensors.size(); ++i) {
    Device device(devices[i]);
    xla::Shape shape = MakeArrayShapeFromDimensions(
        tensors[i].sizes(),
        XlaHelpers::MakeXlaPrimitiveType(tensors[i].type().scalarType()),
        device.hw_type);
    auto populate_fn =
        [&, i](const xla::ComputationClient::TensorSource& source_tensor,
               void* dest_buffer, size_t dest_buffer_size) {
          PopulateTensorBuffer(tensors[i], source_tensor.shape, dest_buffer,
                               dest_buffer_size);
        };
    source_tensors.emplace_back(std::move(shape), devices[i],
                                std::move(populate_fn));
  }
  return xla::ComputationClient::Get()->TransferToServer(source_tensors);
}

xla::Literal GetTensorLiteral(const at::Tensor& tensor,
                              const xla::Shape* shape) {
  xla::Shape computed_shape;
  if (shape == nullptr) {
    auto dimensions = XlaHelpers::I64List(tensor.sizes());
    computed_shape = MakeTorchTensorLayout(
        dimensions,
        XlaHelpers::MakeXlaPrimitiveType(tensor.type().scalarType()));
    shape = &computed_shape;
  }
  xla::Literal literal(*shape);
  PopulateTensorBuffer(tensor, *shape, literal.untyped_data(),
                       literal.size_bytes());
  return literal;
}

std::vector<xla::Shape> GetComponentShapes(const xla::Shape& shape) {
  std::vector<xla::Shape> component_shapes;
  if (shape.IsTuple()) {
    for (const xla::Shape& component_shape : shape.tuple_shapes()) {
      XLA_CHECK(!component_shape.IsTuple()) << shape;
      component_shapes.push_back(component_shape);
    }
  } else {
    component_shapes.push_back(shape);
  }
  return component_shapes;
}

xla::Shape MakeShapeWithDeviceLayout(const xla::Shape& shape,
                                     DeviceType device_type) {
  std::vector<xla::Shape> shape_components = GetComponentShapes(shape);
  std::vector<xla::Shape> shape_components_with_layout;
  XLA_CHECK(!shape_components.empty());
  for (const auto& shape_component : shape_components) {
    std::vector<int64_t> shape_component_dimensions(
        shape_component.dimensions().begin(),
        shape_component.dimensions().end());
    shape_components_with_layout.push_back(MakeArrayShapeFromDimensions(
        shape_component_dimensions, shape_component.element_type(),
        device_type));
  }
  return shape_components_with_layout.size() > 1
             ? xla::ShapeUtil::MakeTupleShape(shape_components_with_layout)
             : shape_components_with_layout.front();
}

}  // namespace torch_xla
