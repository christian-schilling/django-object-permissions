
from django.contrib import admin
import models
from object_permissions.admin import ObjectPermissionsAdmin

class PostAdmin(ObjectPermissionsAdmin):
    
    pass

admin.site.register(models.Post,PostAdmin)
