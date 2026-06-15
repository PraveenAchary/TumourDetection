from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging
from .ml.predict import load_model, predict # Import your functions

logger = logging.getLogger(__name__)

# Load the model once when the server starts
model = load_model()

@api_view(['POST'])
def Predict(request):
    name = request.data.get("username", "").strip()
    image_file = request.FILES.get("image")

    if not name or not image_file:
        return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Pass the file directly to your predict function
        # Your predict function handles Image.open() internally
        result = predict(image_file, model)
        
        return Response({
            "user": name,
            "prediction": result
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Prediction Error: {str(e)}")
        return Response({"error": "Inference failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)