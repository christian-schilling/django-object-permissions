from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from object_permissions.models import UserObjectPermission
from object_permissions.models import GroupObjectPermission

class UserPermissionInline(generic.GenericTabularInline):
    model = UserObjectPermission
class GroupPermissionInline(generic.GenericTabularInline):
    model = GroupObjectPermission

def check_inline_perm(user,inline):
    opts = inline.model._meta
    return (user.has_perm(opts.app_label+'.'+opts.get_change_permission())
        and user.has_perm(opts.app_label+'.'+opts.get_add_permission())
        and user.has_perm(opts.app_label+'.'+opts.get_delete_permission()))

class ObjectPermissionsAdmin(admin.ModelAdmin):

    def __init__(self,model,admin_site):
        self.inlines = [i for i in self.inlines+[UserPermissionInline,GroupPermissionInline]]
        retval = super(ObjectPermissionsAdmin,self).__init__(model,admin_site)
        self.all_inline_instances = self.inline_instances
        return retval

    def queryset(self,request):
        return UserObjectPermission.objects.changeable(self.model,request.user)

    def is_changeable(self,model,object_id,request):
        return UserObjectPermission.objects.is_changeable(self.model,object_id,request.user)

    def is_deleteable(self,model,object_id,request):
        return UserObjectPermission.objects.is_deleteable(self.model,object_id,request.user)

    def has_change_permission(self,request,object=None):
        any = super(ObjectPermissionsAdmin,self).has_change_permission(request,object)
        if not object:
            return any
        else:
            return any and self.is_changeable(self.model,object.id,request)

    def has_delete_permission(self,request,object=None):
        any = super(ObjectPermissionsAdmin,self).has_delete_permission(request,object)
        if not object:
            return any
        else:
            return any and self.is_deleteable(self.model,object.id,request)

    def add_view(self,request,*args,**kwargs):
        self.inline_instances = [i for i in self.all_inline_instances
                                    if check_inline_perm(request.user,i)]
        return super(ObjectPermissionsAdmin,self).add_view(request,*args,**kwargs)

    def change_view(self,request,object_id,extra_context=None):
        self.inline_instances = [i for i in self.all_inline_instances
                                    if check_inline_perm(request.user,i)]
        if self.is_changeable(self.model,object_id,request):
            return super(ObjectPermissionsAdmin,self).change_view(request,object_id,extra_context)
        raise PermissionDenied

    def delete_view(self,request,object_id,extra_context=None):
        if self.is_deleteable(self.model,object_id,request):
            return super(ObjectPermissionsAdmin,self).delete_view(request,object_id,extra_context)
        raise PermissionDenied


    def save_model(self, request, obj, form, change):
        super(ObjectPermissionsAdmin,self).save_model(request,obj,form,change)
        if change:
            return
        UserObjectPermission.objects.create(
            user=request.user,
            can_change=True,
            can_delete=True,
            subject=obj
        )
        try:
            sitegroup = Group.objects.get(name=Site.objects.get_current().domain)
            GroupObjectPermission.objects.create(
                group=sitegroup,
                can_change=True,
                can_delete=True,
                subject=obj,
            )
        except:
            pass
