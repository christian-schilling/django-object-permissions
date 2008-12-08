
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


class ObjectPermission(models.Model):
    can_change = models.BooleanField()
    can_delete = models.BooleanField()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    subject = generic.GenericForeignKey()

    class Meta:
        abstract = True

class GroupObjectPermission(ObjectPermission):
    group = models.ForeignKey('auth.Group')

class UserObjectPermissionManager(models.Manager):
    def is_changeable(self,model,object_id,user):
        if user.is_superuser: return True
        ct_type = ContentType.objects.get_for_model(model)
        if self.model.objects.filter(
                content_type=ct_type,
                object_id=object_id,
                user=user,
                can_change=True,
            ).count():
            return True
        groupids = set(user.groups.all().values_list("id",flat=True))
        if GroupObjectPermission.objects.filter(
            content_type=ct_type,
            group__in=groupids,
            can_change=True,
        ).count():
            return True
        return False

    def is_deleteable(self,model,object_id,user):
        if user.is_superuser: return True
        ct_type = ContentType.objects.get_for_model(model)
        if self.model.objects.filter(
                content_type=ct_type,
                object_id=object_id,
                user=user,
                can_change=True,
                can_delete=True,
            ).count():
            return True
        groupids = set(user.groups.all().values_list("id",flat=True))
        if GroupObjectPermission.objects.filter(
            content_type=ct_type,
            group__in=groupids,
            can_change=True,
            can_delete=True,
        ).count():
            return True
        return False

    def changeable(self,model,user):
        if user.is_superuser: return model.objects.all()
        ct_type = ContentType.objects.get_for_model(model)
        userperms = self.model.objects.filter(
            content_type=ct_type,
            user=user,
            can_change=True,
        ).values_list("object_id",flat=True)
        groupids = set(user.groups.all().values_list("id",flat=True))
        groupperms = GroupObjectPermission.objects.filter(
            content_type=ct_type,
            group__in=groupids,
            can_change=True,
        ).values_list("object_id",flat=True)
        import pdb
        ids = set(userperms) | set(groupperms)
        return model.objects.filter(id__in=ids)
        

class UserObjectPermission(ObjectPermission):
    user = models.ForeignKey('auth.User')
    objects = UserObjectPermissionManager()



