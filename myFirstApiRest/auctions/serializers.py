from rest_framework import serializers
from .models import Category, Auction, Bid, Rating, Comment
from drf_spectacular.utils import extend_schema_field
from django.utils import timezone
from datetime import timedelta



class CategoryListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']

class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AuctionListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    closing_date = serializers.DateTimeField(input_formats=["%Y-%m-%dT%H:%M"])
    isOpen = serializers.SerializerMethodField(read_only=True)
    auctioneer_username = serializers.CharField(source='auctioneer.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    thumbnail = serializers.URLField(required=False, allow_blank=True, allow_null=True)


    class Meta:
        model = Auction
        fields = [
        'id', 'title', 'description', 'creation_date', 'closing_date',
        'thumbnail', 'price', 'stock', 'brand', 'category',
        'isOpen', 'auctioneer_username', 'category_name'
        ]
        read_only_fields = ['rating']
    @extend_schema_field(serializers.BooleanField()) 
    def get_isOpen(self, obj):
        return obj.closing_date > timezone.now()
    def validate_closing_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Closing date must be greater than now.")
        if value - timezone.now() < timedelta(days=15):
            raise serializers.ValidationError("Closing date must be at least 15 days after creation date.")
        return value
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['auctioneer'] = request.user
        return super().create(validated_data)



class AuctionDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    isOpen = serializers.SerializerMethodField(read_only=True)
    auctioneer_username = serializers.CharField(source='auctioneer.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = Auction
        fields = '__all__'
    @extend_schema_field(serializers.BooleanField()) 
    def get_isOpen(self, obj):
        return obj.closing_date > timezone.now()
    def validate_closing_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Closing date must be greater than now.")
        
        fecha_creacion = self.initial_data.get('creation_date', timezone.now())
        if fecha_creacion and (value - fecha_creacion) < timedelta(days=15):
            raise serializers.ValidationError("Closing date must be at least 15 days after creation date.")
        
        return value
    
class BidListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    bidder_username = serializers.CharField(source='bidder.username', read_only=True)

    class Meta:
        model = Bid
        fields = ['id', 'auction', 'price', 'creation_date', 'bidder','bidder_username']
        read_only_fields = ['auction','bidder']

class BidDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    bidder_username = serializers.CharField(source='bidder.username', read_only=True)

    class Meta:
        model = Bid
        fields = ['id', 'auction', 'price', 'creation_date', 'bidder','bidder_username']
        read_only_fields = ['auction','bidder']

class RatingListCreateSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'auction', 'user', 'user_username','value']
        read_only_fields = ['user','auction']


class CommentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    auction_id = serializers.IntegerField(read_only=True)
    auction_title = serializers.CharField(source='auction.title', read_only=True)
    auction_price = serializers.DecimalField(source='auction.price', max_digits=10, decimal_places=2, read_only=True)
    auction_category = serializers.CharField(source='auction.category.name', read_only=True)
    auction_closing_date = serializers.CharField(source='auction.closing_date', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'title', 'content', 'created_at', 'updated_at',
            'user', 'user_username', 'auction', 'auction_id',
            'auction_title', 'auction_price', 'auction_category', 'auction_closing_date'
        ]
        read_only_fields = ['user', 'auction', 'created_at', 'updated_at']
