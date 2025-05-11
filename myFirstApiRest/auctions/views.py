from django.shortcuts import render
from rest_framework import generics, status
from .models import Category, Auction, Bid,Rating
from .serializers import CategoryListCreateSerializer, CategoryDetailSerializer, AuctionListCreateSerializer, AuctionDetailSerializer, BidDetailSerializer, BidListCreateSerializer, RatingListCreateSerializer
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from .permisions import IsOwnerOrAdmin, IsBidOwnerOrAdmin





class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all() # Que dato tengo que devolver
    serializer_class = CategoryListCreateSerializer # Como lo devuelvo
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # cualquier usuario puede ver
        return [IsAdminUser()] 

class CategoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer
    permission_classes = [IsAdminUser]

class AuctionListCreate(generics.ListCreateAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionListCreateSerializer
    permission_classes = [AllowAny] 
    def get_queryset(self):
        queryset = Auction.objects.all()
        params = self.request.query_params
        search = params.get('search', None)
        if search and len(search) < 3:
            raise ValidationError(
                {"search": "Search query must be at least 3 characters long."}, code=status.HTTP_400_BAD_REQUEST)

        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))
        category_id = params.get('category', None)
        if category_id:
            if not Category.objects.filter(id=category_id).exists():
                raise ValidationError(
                    {"category": "Category must be a valid category id."}, code=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(category_id=category_id)
        
        # Filtrado por rango de precios
        price_min = params.get('price_min', None)
        price_max = params.get('price_max', None)

        if price_min and not price_min.isdigit():
            raise ValidationError({"price_min": "Price minimum must be a natural number greater than 0."}, 
                                   code=status.HTTP_400_BAD_REQUEST)
        if price_max and not price_max.isdigit():
            raise ValidationError({"price_max": "Price maximum must be a natural number greater than 0."}, 
                                   code=status.HTTP_400_BAD_REQUEST)

        price_min = int(price_min) if price_min else None
        price_max = int(price_max) if price_max else None

        if price_min and price_max and price_min >= price_max:
            raise ValidationError({"price_max": "Price maximum must be greater than price minimum."}, 
                                   code=status.HTTP_400_BAD_REQUEST)

        if price_min:
            queryset = queryset.filter(price__gte=price_min)  # Usamos 'price' en lugar de 'starting_price'
        if price_max:
            queryset = queryset.filter(price__lte=price_max)  # Usamos 'price' en lugar de 'starting_price'

        return queryset
    
    def perform_create(self, serializer):
        serializer.save(auctioneer=self.request.user)


class AuctionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdmin] 
    queryset = Auction.objects.all()
    serializer_class = AuctionDetailSerializer

class BidListCreate(generics.ListCreateAPIView):
    serializer_class = BidListCreateSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Bid.objects.filter(auction_id=self.kwargs['auction_id'])

    def perform_create(self, serializer):
        auction_id = self.kwargs['auction_id']
        serializer.save(auction_id=auction_id, bidder=self.request.user)


class BidRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BidDetailSerializer
    permission_classes = [IsBidOwnerOrAdmin]

    def get_queryset(self):
        return Bid.objects.filter(auction_id=self.kwargs['auction_id'])
    

class UserAuctionListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AuctionListCreateSerializer
    def get(self, request, *args, **kwargs):
    # Obtener las subastas del usuario autenticado
        user_auctions = Auction.objects.filter(auctioneer=request.user)
        serializer = AuctionListCreateSerializer(user_auctions, many=True)
        return Response(serializer.data)
    
# AÑADIR AQUI LA LOGICA DE MODIFICAR, ELIMINAR SUBASTA
# AÑADIR EL CALCULO DE LA MEDIA


