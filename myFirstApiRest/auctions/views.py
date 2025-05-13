from django.shortcuts import render
from rest_framework import generics, status
from .models import Category, Auction, Bid, Rating, Comment
from .serializers import CategoryListCreateSerializer, CategoryDetailSerializer, AuctionListCreateSerializer, AuctionDetailSerializer, BidDetailSerializer, BidListCreateSerializer, RatingListCreateSerializer, CommentSerializer
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from .permisions import IsOwnerOrAdmin, IsBidOwnerOrAdmin
from django.db.models import Avg
from drf_spectacular.utils import extend_schema



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
        user_auctions = Auction.objects.filter(auctioneer=request.user)
        serializer = AuctionListCreateSerializer(user_auctions, many=True)
        return Response(serializer.data)
    

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Comment.objects.filter(auction_id=self.kwargs['auction_id'])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, auction_id=self.kwargs['auction_id'])


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        return Comment.objects.filter(auction_id=self.kwargs['auction_id'])


# class RatingListCreate(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, auction_id):
#         ratings = Rating.objects.filter(auction_id=auction_id)
#         avg = ratings.aggregate(avg=Avg('value'))['avg']
#         return Response({"average_rating": round(avg, 2) if avg else None})
    
#     @extend_schema(request=RatingListCreateSerializer) 
#     def post(self, request, auction_id):
#         data = request.data.copy()
#         data['auction'] = auction_id  # asignamos la subasta al cuerpo del request
#         serializer = RatingListCreateSerializer(data=data, context={'request': request})
#         serializer.is_valid(raise_exception=True)

#         rating, created = Rating.objects.update_or_create(
#             user=request.user,
#             auction_id=auction_id,
#             defaults={'value': serializer.validated_data['value']}
#         )

#         return Response(RatingListCreateSerializer(rating).data, status=201 if created else 200)


#     def delete(self, request, auction_id):
#         try:
#             rating = Rating.objects.get(user=request.user, auction_id=auction_id)
#             rating.delete()
#             return Response(status=204)
#         except Rating.DoesNotExist:
#             return Response({"detail": "Rating not found."}, status=404)
class RatingListCreate(generics.ListCreateAPIView):
    serializer_class = RatingListCreateSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Rating.objects.filter(auction_id=self.kwargs['auction_id'])

    def perform_create(self, serializer):
        auction_id = self.kwargs['auction_id']
        value = serializer.validated_data['value']
        rating, created = Rating.objects.update_or_create(
            user=self.request.user,
            auction_id=auction_id,
            defaults={'value': value}
        )
        self._rating_instance = rating
        self.update_mean(auction_id)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        serializer = self.get_serializer(self._rating_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update_mean(self, auction_id):
        auction = Auction.objects.get(pk=auction_id)
        ratings = Rating.objects.filter(auction_id=auction_id)
        avg = ratings.aggregate(Avg('value'))['value__avg']
        auction.rating = round(avg, 2) if avg else 0
        auction.save()
        



class RatingRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RatingListCreateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return Rating.objects.filter(auction_id=self.kwargs['auction_id'])
    def perform_update(self, serializer):
        instance = serializer.save()
        self.update_mean(instance.auction_id)

    def perform_destroy(self, instance):
        auction_id = instance.auction_id
        instance.delete()
        self.update_mean(auction_id)

    def update_mean(self, auction_id):
        auction = Auction.objects.get(pk=auction_id)
        avg = Rating.objects.filter(auction_id=auction_id).aggregate(Avg('value'))['value__avg']
        auction.rating = round(avg, 2) if avg else 0
        auction.save()

class UserRatingDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, auction_id):
        try:
            rating = Rating.objects.get(user=request.user, auction_id=auction_id)
            serializer = RatingListCreateSerializer(rating)
            return Response(serializer.data, status=200)
        except Rating.DoesNotExist:
            return Response({"detail": "No rating found"}, status=404)