from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

# DO NOT LOAD MODEL HERE. 
# Global initialization is crashing you because of memory limits.

@api_view(['POST'])
def Predict(request):
    # IMPORT INSIDE THE FUNCTION (Lazy Import)
    # This prevents them from being in RAM 24/7
    import torch
    import torch.nn as nn
    from torchvision import models
    from .ml.predict import load_model, predict

    # Load model inside the function
    # Note: To avoid re-loading for every request, use a simple check:
    if not hasattr(Predict, "model"):
        Predict.model = load_model()

    name = request.data.get("username", "").strip()
    image_file = request.FILES.get("image")

    if not name or not image_file:
        return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        result = predict(image_file, Predict.model)
        return Response({"user": name, "prediction": result}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Prediction Error: {str(e)}")
        return Response({"error": "Inference failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
