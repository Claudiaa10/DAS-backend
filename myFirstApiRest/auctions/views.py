from rest_framework import generics,status
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from .models import Category, Auction, Bid
from .serializers import CategoryListCreateSerializer, CategoryDetailSerializer, AuctionListCreateSerializer, AuctionDetailSerializer, BidDetailSerializer, BidListCreateSerializer

class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListCreateSerializer

class CategoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer

class AuctionListCreate(generics.ListCreateAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionListCreateSerializer

    def get_queryset(self):
        queryset = Auction.objects.all()
        params = self.request.query_params
        search = params.get('search', None)
        # category_id = params.get("category",None)
        # min_price = params.get("min_price",None)
        # max_price = params.get("max_price",None)
        if search and len(search) < 3: # Validación
            raise ValidationError(
            {"search": "Search query must be at least 3 characters long."},
            code=status.HTTP_400_BAD_REQUEST 
            )
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))
        # if category_id:
        #     if not category_id.isdigit():
        #         raise ValidationError
        #     if not Category.objects.filter(id = category_id).exists():
        #         raise ValidationError
        #     queryset = query_set.filter({id:validation_id})
        return queryset

class AuctionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionDetailSerializer

class BidListCreate(generics.ListCreateAPIView):
    serializer_class = BidListCreateSerializer

    def get_queryset(self):
        auction_id = self.kwargs["auction_id"]
        return Bid.objects.filter(auction_id=auction_id)

    def perform_create(self, serializer):
        auction_id = self.kwargs["auction_id"]
        serializer.save(auction_id=auction_id)

class BidRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BidDetailSerializer

    def get_queryset(self):
        auction_id = self.kwargs["auction_id"]
        return Bid.objects.filter(auction_id=auction_id)