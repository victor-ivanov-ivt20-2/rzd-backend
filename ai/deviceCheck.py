import torch

import ultralytics
ultralytics.checks()

print("mkl", torch.has_mkl)
print("mps", torch.has_mps)
print("cuda", torch.cuda.is_available())
print("cudnn", torch.has_cudnn)
print("lapack", torch.has_lapack)
print("mkldnn", torch.has_mkldnn)
print("openmp", torch.has_openmp)
print("spectral", torch.has_spectral)
