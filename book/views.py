from rest_framework import viewsets
from .models import Book
from .permissions import IsAdminALLORIsAuthenticatedReadOnly
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminALLORIsAuthenticatedReadOnly,)
