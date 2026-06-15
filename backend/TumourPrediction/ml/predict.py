import os
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image

# ─────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────

CLASS_NAMES = ['glioma', 'meningioma', 'notumor', 'pituitary']  # must match training order

MODEL_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'best_model.pth')

DEVICE = torch.device('cpu')

# ─────────────────────────────────────────────────────────────────
# TRANSFORM — same as test transform used during training
# ─────────────────────────────────────────────────────────────────

transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# ─────────────────────────────────────────────────────────────────
# LOAD MODEL — called once at startup, reused for every request
# ─────────────────────────────────────────────────────────────────

def load_model():
    model = models.resnet18(weights=None)

    # Freeze early layers (must mirror training setup)
    for param in model.parameters():
        param.requires_grad = False

    for param in model.layer3.parameters():
        param.requires_grad = True

    for param in model.layer4.parameters():
        param.requires_grad = True

    # Replace output layer — same as training
    model.fc = nn.Linear(model.fc.in_features, len(CLASS_NAMES))

    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model


# ─────────────────────────────────────────────────────────────────
# PREDICT — accepts a PIL Image or a file path
# Returns: { 'class': str, 'confidence': float, 'all_scores': dict }
# ─────────────────────────────────────────────────────────────────

def predict(image_input, model):
    """
    image_input: PIL.Image or str (file path)
    model:       loaded model from load_model()
    """
    
    if isinstance(image_input, str):
        image = Image.open(image_input).convert('RGB')
    else:
        image = Image.open(image_input).convert('RGB')

    tensor = transform(image).unsqueeze(0).to(DEVICE)   # shape: (1, 3, 128, 128)

    with torch.no_grad():
        outputs     = model(tensor)                      # raw logits
        probs       = torch.softmax(outputs, dim=1)[0]  # probabilities
        pred_idx    = probs.argmax().item()
        confidence  = probs[pred_idx].item()

    all_scores = {
        CLASS_NAMES[i]: round(probs[i].item() * 100, 2)
        for i in range(len(CLASS_NAMES))
    }

    return {
        'class':      CLASS_NAMES[pred_idx],
        'confidence': round(confidence * 100, 2),
        'all_scores': all_scores,
    }


# ─────────────────────────────────────────────────────────────────
# QUICK TEST — run this file directly to check everything works
# Usage: python predict.py path/to/test_image.jpg
# ─────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python predict.py <image_path>")
        sys.exit(1)

    img_path = sys.argv[1]
    print(f"Loading model from: {MODEL_PATH}")
    _model = load_model()
    print("Model loaded.\n")

    result = predict(img_path, _model)
    print(f"Prediction : {result['class']}")
    print(f"Confidence : {result['confidence']}%")
    print(f"All scores : {result['all_scores']}")