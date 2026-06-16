from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def Predict(request):
    import torch
    import torch.nn as nn
    from torchvision import models
    from .ml.predict import load_model, predict

    # Load model once, cache on function object
    if not hasattr(Predict, "model"):
        Predict.model = load_model()

    name       = request.data.get("username", "").strip()
    image_file = request.FILES.get("image")

    if not name or not image_file:
        return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        result = predict(image_file, Predict.model)
        # result already contains: class, confidence, all_scores
        return Response({
            "user":       name,
            "prediction": result   # { class, confidence, all_scores }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Prediction Error: {str(e)}")
        return Response({"error": "Inference failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
