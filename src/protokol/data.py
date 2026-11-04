from __future__ import annotations
import numpy as np

TUGAS = "regresi"

def muat():
    print("Memuat dataset dummy (simulasi sementara Numpy)...")
    X_train = np.random.randn(100, 30, 64, 64).astype(np.float32)
    y_train = (np.random.rand(100, 1) * 255).astype(np.float32)
    
    X_val = np.random.randn(20, 30, 64, 64).astype(np.float32)
    y_val = (np.random.rand(20, 1) * 255).astype(np.float32)
    
    X_test = np.random.randn(20, 30, 64, 64).astype(np.float32)
    y_test = (np.random.rand(20, 1) * 255).astype(np.float32)
    
    return X_train, y_train, X_val, y_val, X_test, y_test