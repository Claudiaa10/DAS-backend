from django.urls import path
from .views import CategoryListCreate, CategoryRetrieveUpdateDestroy, AuctionListCreate, AuctionRetrieveUpdateDestroy, BidListCreate, BidRetrieveUpdateDestroy, UserAuctionListView, CommentListCreateView, CommentRetrieveUpdateDestroyView, RatingListCreate, RatingRetrieveUpdateDestroy,UserRatingDetail
app_name="auctions"
urlpatterns = [
    path('categories/', CategoryListCreate.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryRetrieveUpdateDestroy.as_view(), name='category-detail'),
    path('', AuctionListCreate.as_view(), name='auction-list-create'),
    path('<int:pk>/', AuctionRetrieveUpdateDestroy.as_view(), name='auction-detail'),
    path('<int:auction_id>/bid/', BidListCreate.as_view(), name='bid-list-create'),
    path('<int:auction_id>/bid/<int:pk>/', BidRetrieveUpdateDestroy.as_view(), name='bid-detail'),
    path('users/', UserAuctionListView.as_view(), name='action-from-users'),
    path('myAuctions/',UserAuctionListView.as_view(),name ="user-auctions" ),
    path('<int:auction_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('<int:auction_id>/comments/<int:pk>/', CommentRetrieveUpdateDestroyView.as_view(), name='comment-detail'),
    path('<int:auction_id>/rating/', RatingListCreate.as_view(), name='auction-rating'),
    path('<int:auction_id>/ratings/<int:pk>/', RatingRetrieveUpdateDestroy.as_view(), name='rating-detail'),
    path('<int:auction_id>/rating/user/', UserRatingDetail.as_view(), name='user-rating'),
]
