from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, blank=False, unique=True)

    class Meta:
        ordering=('id',)
    def __str__(self):
        return self.name
    
class Auction(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=2, validators=[
            MinValueValidator(0), MaxValueValidator(5)],default=0)
    stock = models.IntegerField(validators=[MinValueValidator(1)])
    brand = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name='auctions', on_delete=models.CASCADE)
    thumbnail = models.URLField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateTimeField()
    auctioneer = models.ForeignKey(CustomUser, related_name='auctions', on_delete=models.CASCADE)


    class Meta:
        ordering=('id',)
    def __str__(self):
        return self.title
    

class Bid(models.Model):
    auction = models.ForeignKey(Auction, related_name='bids', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    creation_date = models.DateTimeField(auto_now_add=True)
    bidder = models.ForeignKey(CustomUser, related_name='bids', on_delete=models.CASCADE)
    class Meta:
        ordering = ('id',)

    def __str__(self):
        return f"Puja de {self.bidder} por {self.price}€ en {self.auction.title}"

class Rating(models.Model):
    auction = models.ForeignKey(Auction, related_name="ratings",on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser,related_name="ratings",on_delete=models.CASCADE)
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    class Meta:
        unique_together = ("user","auction")
        ordering = ('id',)
    def __str__(self):
        return f"Rating de {self.user} en {self.auction} con valor de {self.value}"
    
    

class Comment(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(CustomUser, related_name='comments', on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, related_name='comments', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username} en {self.auction.title}"
