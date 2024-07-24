from django.db import models

class Query(models.Model):
    user_query = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class OffensiveWord(models.Model):
    word = models.CharField(max_length=255)
