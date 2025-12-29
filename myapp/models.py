from django.db import models

class RegisteredPlate(models.Model):
    """
    Represents a 'valid' license plate in the police database.
    Used to benchmark Database Lookup Speed vs DFA Algorithm Speed.
    """
    # We use a distinct index to make lookups faster (O(log N)), 
    # but it will still be slower than DFA (O(L)) under load.
    plate_number = models.CharField(max_length=15, unique=True, db_index=True)
    owner_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.plate_number