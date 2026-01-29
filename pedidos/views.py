from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.detector import detect_personal_data


class ClassificarPedidoView(APIView):
    """
    API para classificar se um pedido contém dados pessoais.
    
    POST /classificar-pedido/
    Body: {"texto": "Texto do pedido..."}
    
    Response: {
        "contem_dados_pessoais": true/false,
        "metodo": "regex" ou "ml",
        "tipos_detectados": ["CPF", "Email", ...],
        "confianca": 0.0-1.0
    }
    """
    
    def post(self, request):
        texto = request.data.get('texto')
        
        if not texto:
            return Response(
                {'erro': 'Campo "texto" é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resultado = detect_personal_data(texto)
        
        return Response(resultado, status=status.HTTP_200_OK)