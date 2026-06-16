import os
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import torchvision.models as models
from torch.utils.data import DataLoader, Subset
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import numpy as np

# ─────────────────────────────────────────────────────────────────
# DYNAMIC PATHS
# ─────────────────────────────────────────────────────────────────

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))   # ml/
ML_DIR      = os.path.dirname(BASE_DIR)                    # TumourPrediction/
BACKEND_DIR = os.path.dirname(ML_DIR)                      # backend/
PROJECT_DIR = os.path.dirname(BACKEND_DIR)                 # E:/Django/TumourPrediction/
DATA_DIR    = os.path.join(os.path.dirname(PROJECT_DIR), 'Datasets', 'MRI Images', 'Data')

TRAIN_DIR   = os.path.join(DATA_DIR, 'Training')
TEST_DIR    = os.path.join(DATA_DIR, 'Testing')

print(f"Train path : {TRAIN_DIR}")
print(f"Test path  : {TEST_DIR}")

# ─────────────────────────────────────────────────────────────────
# TRANSFORMS
# 128x128 instead of 224x224 — ResNet18 works fine with this.
# It was trained on 224x224 but does NOT require it.
# Smaller size = much faster on CPU. Small accuracy tradeoff.
# ─────────────────────────────────────────────────────────────────

transform_train = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

transform_test = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# ─────────────────────────────────────────────────────────────────
# DATASET — 85% train, 15% validation, separate test
# ─────────────────────────────────────────────────────────────────

full_train_aug   = torchvision.datasets.ImageFolder(root=TRAIN_DIR, transform=transform_train)
full_train_clean = torchvision.datasets.ImageFolder(root=TRAIN_DIR, transform=transform_test)

total         = len(full_train_aug)
train_size    = int(0.85 * total)
val_size      = total - train_size

indices       = torch.randperm(total).tolist()
train_indices = indices[:train_size]
val_indices   = indices[train_size:]

train_dataset = Subset(full_train_aug,   train_indices)   # augmented
val_dataset   = Subset(full_train_clean, val_indices)     # clean
test_dataset  = torchvision.datasets.ImageFolder(root=TEST_DIR, transform=transform_test)

print(f"\nDataset sizes:")
print(f"  Train      : {len(train_dataset)} images")
print(f"  Validation : {len(val_dataset)} images")
print(f"  Test       : {len(test_dataset)} images")

# ─────────────────────────────────────────────────────────────────
# DATA LOADERS
# batch_size=16 → less memory pressure on CPU
# num_workers=2 → 2 CPU cores load images in parallel
# ─────────────────────────────────────────────────────────────────

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True,  num_workers=0)
val_loader   = DataLoader(val_dataset,   batch_size=16, shuffle=False, num_workers=0)
test_loader  = DataLoader(test_dataset,  batch_size=16, shuffle=False, num_workers=0)

class_names = full_train_aug.classes
num_classes = len(class_names)
print(f"\nClasses ({num_classes}): {class_names}")

device = torch.device('cpu')
print(f"Device: CPU")

# ─────────────────────────────────────────────────────────────────
# MODEL — ResNet18 (as requested)
#
# ResNet18 layer structure:
#   conv1, bn1   → very early  (edges, gradients)      → FREEZE
#   layer1       → early       (basic textures)         → FREEZE
#   layer2       → early-mid   (simple shapes)          → FREEZE
#   layer3       → mid-deep    (complex patterns)       → UNFREEZE
#   layer4       → deep        (high level concepts)    → UNFREEZE
#   fc           → output                               → REPLACE
# ─────────────────────────────────────────────────────────────────

model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

# Step 1: Freeze everything
for param in model.parameters():
    param.requires_grad = False

# Step 2: Unfreeze deeper layers — relearn MRI specific patterns
for param in model.layer3.parameters():
    param.requires_grad = True

for param in model.layer4.parameters():
    param.requires_grad = True

# Step 3: Replace output layer — 4 tumor classes
model.fc = nn.Linear(model.fc.in_features, num_classes)

model = model.to(device)

# ─────────────────────────────────────────────────────────────────
# LOSS AND OPTIMIZER
# ─────────────────────────────────────────────────────────────────

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(
    filter(lambda p: p.requires_grad, model.parameters()),
    lr=1e-4
)

scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', patience=2, factor=0.1
)

# ─────────────────────────────────────────────────────────────────
# TRAIN FUNCTION — with batch progress bar
# ─────────────────────────────────────────────────────────────────

def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    correct    = 0
    total_loss = 0
    total      = len(loader)

    for batch_idx, (images, labels) in enumerate(loader):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss    = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        correct    += (outputs.argmax(1) == labels).sum().item()

        done = int(30 * (batch_idx + 1) / total)
        print(f"\r  Batch {batch_idx+1}/{total} [{'█'*done}{'░'*(30-done)}]", end='')

    print()
    return total_loss / len(loader), correct / len(loader.dataset) * 100

# ─────────────────────────────────────────────────────────────────
# EVALUATE FUNCTION
# ─────────────────────────────────────────────────────────────────

'''
This is what validation does. After every epoch, we check — is the model actually generalizing, or just memorizing training images?
We also use validation to make decisions like:

When to stop training
When to save the best model
Whether to reduce the learning rate
'''
def evaluate(model, loader, criterion, device):
    model.eval()
    correct    = 0
    total_loss = 0

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss    = criterion(outputs, labels)
            total_loss += loss.item()
            correct    += (outputs.argmax(1) == labels).sum().item()

    return total_loss / len(loader), correct / len(loader.dataset) * 100

# ─────────────────────────────────────────────────────────────────
# TRAINING LOOP
# ─────────────────────────────────────────────────────────────────

EPOCHS          = 5
best_val_acc    = 0.0
MODEL_SAVE_PATH = os.path.join(BASE_DIR, 'best_model.pth')

train_accs   = []
val_accs     = []
train_losses = []
val_losses   = []

print("\nStarting Training (ResNet18 — CPU optimized)...")
print("─" * 65)

for epoch in range(EPOCHS):
    print(f"\nEpoch {epoch+1}/{EPOCHS}")
    train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
    val_loss,   val_acc   = evaluate(model, val_loader, criterion, device)

    train_accs.append(train_acc)
    val_accs.append(val_acc)
    train_losses.append(train_loss)
    val_losses.append(val_loss) 

    scheduler.step(val_loss)

    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), MODEL_SAVE_PATH)
        saved = "  ✓ best model saved"
    else:
        saved = ""

    print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
    print(f"  Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%{saved}")

print("\n" + "─" * 65)
print(f"Best Validation Accuracy: {best_val_acc:.2f}%")

# ─────────────────────────────────────────────────────────────────
# FINAL TEST — load best model, run once on test set
# ─────────────────────────────────────────────────────────────────

print("\nLoading best model for final test evaluation...")
model.load_state_dict(torch.load(MODEL_SAVE_PATH))
test_loss, test_acc = evaluate(model, test_loader, criterion, device)
print(f"Final Test Accuracy: {test_acc:.2f}%")

# ─────────────────────────────────────────────────────────────────
# PLOTS
# ─────────────────────────────────────────────────────────────────

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.plot(train_accs, marker='o', label='Train Accuracy')
ax1.plot(val_accs,   marker='o', label='Val Accuracy')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Accuracy (%)')
ax1.set_title('Train vs Validation Accuracy')
ax1.legend()

ax2.plot(train_losses, marker='o', label='Train Loss')
ax2.plot(val_losses,   marker='o', label='Val Loss')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Loss')
ax2.set_title('Train vs Validation Loss')
ax2.legend()

plt.suptitle('Brain MRI Tumor — ResNet18 Transfer Learning (CPU)')
plt.tight_layout()
plt.show()

# ─────────────────────────────────────────────────────────────────
# CONFUSION MATRIX
# ─────────────────────────────────────────────────────────────────

model.eval()
all_preds  = []
all_labels = []

with torch.no_grad():
    for images, labels in test_loader:
        images  = images.to(device)
        outputs = model(images)
        preds   = outputs.argmax(1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(labels.numpy())

cm   = confusion_matrix(all_labels, all_preds)
disp = ConfusionMatrixDisplay(cm, display_labels=class_names)
disp.plot(cmap='Blues')
plt.title('Brain MRI Tumor — Confusion Matrix (Test Set)')
plt.show()
