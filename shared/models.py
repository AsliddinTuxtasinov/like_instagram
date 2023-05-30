import uuid

from django.db import models


# Base model class that provides common fields and functionalities for other models to inherit from
class BaseModel(models.Model):
    # Unique identifier for each instance of the model
    id = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, primary_key=True)

    # DateTimeField that automatically stores the creation time of an instance when it is first saved to the database
    created_time = models.DateTimeField(auto_now_add=True)

    # DateTimeField that automatically updates with the current time whenever the instance is saved or updated in the
    # database
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        # Specifies that this model is abstract, meaning it won't be created as a separate table in the database
        abstract = True
