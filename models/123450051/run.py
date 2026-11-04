import sys
import os
import argparse
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.protokol import data

class KipasCNN(nn.Module):
    def __init__(self):
        super(KipasCNN, self).__init__()
        self.conv1 = nn.Conv2d(30, 16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc = nn.Linear(16 * 32 * 32, 1)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    torch.manual_seed(args.seed)
    
    # 1. Terima 6 keluaran dari data.muat()
    X_train, y_train, X_val, y_val, X_test, y_test = data.muat() 
    
    # 2. Ubah data Validasi menjadi DataLoader PyTorch
    tensor_X_val = torch.from_numpy(X_val)
    tensor_y_val = torch.from_numpy(y_val)
    val_loader = DataLoader(TensorDataset(tensor_X_val, tensor_y_val), batch_size=8)
    
    # 3. Prediksi
    model = KipasCNN()
    model.eval()
    prediksi_val = []
    
    print("Melakukan prediksi pada data validasi...")
    with torch.no_grad():
        for inputs, targets in val_loader:
            outputs = model(inputs)
            prediksi_val.append(outputs.numpy())
            
    prediksi_val = np.concatenate(prediksi_val, axis=0)

    # 4. Simpan numpy array
    folder_output = f"results/123450051"
    os.makedirs(folder_output, exist_ok=True)
    file_output = f"{folder_output}/pred_val.npy"
    
    np.save(file_output, prediksi_val)
    print(f"Prediksi berhasil disimpan di {file_output}")
    print("Selesai! Silakan jalankan skrip evaluate.py")

if __name__ == '__main__':
    main()