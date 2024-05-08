from django.db import models


class BaseModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(is_deleted=True)


class BaseModelClass(models.Model):
    objects = BaseModelManager()
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=False,
                                      blank=False,
                                      db_index=True)
    updated_at = models.DateTimeField(
        auto_now=True
    )
    is_deleted = models.BooleanField(
        default=False
    )

    class Meta:
        abstract = True
