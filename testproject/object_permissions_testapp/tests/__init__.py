from django.test import TestCase
from django.contrib.auth.models import User,Group,Permission
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

# Import object_permissions_testapp's models
import object_permissions_testapp.models
from object_permissions_testapp.models import *
from object_permissions.models import UserObjectPermission,GroupObjectPermission

class TestObjectPermissions(TestCase):

    def setUp(self):
        self.testuser = User.objects.create_user("testuser","testuser","testuser")
        self.testuser2 = User.objects.create_user("testuser2","testuser2","testuser2")
        self.testgroup = Group.objects.create(name=Site.objects.get_current().domain)
        self.testuser.is_staff = True
        self.testuser2.is_staff = True
        ct_type = ContentType.objects.get_for_model(Post)
        Permission.objects.get(name='Can change post',content_type=ct_type).user_set.add(self.testuser)
        Permission.objects.get(name='Can add post',content_type=ct_type).user_set.add(self.testuser)
        Permission.objects.get(name='Can change post',content_type=ct_type).user_set.add(self.testuser2)
        Permission.objects.get(name='Can add post',content_type=ct_type).user_set.add(self.testuser2)
        self.testuser.save()
        self.testuser2.save()

    def tearDown(self):
        # delete all model instances
        Post.objects.all().delete()
        self.testuser.delete()
        self.testgroup.delete()

    def test_no_permission_change(self):
        result = self.client.login(username="testuser",password="testuser")
        self.assertEqual(result,True)

        p1 = Post.objects.create(title='post1',text='Post1 text')
        response = self.client.get("/admin/object_permissions_testapp/post/%s/"%(p1.pk))
        self.assertEqual(response.status_code,403)

    def test_no_permission_changelist(self):
        result = self.client.login(username="testuser",password="testuser")
        self.assertEqual(result,True)

        p1 = Post.objects.create(title='post1',text='Post1 text')
        response = self.client.get("/admin/object_permissions_testapp/post/")
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"0 posts")

    def test_user_permission_change(self):
        result = self.client.login(username="testuser",password="testuser")
        self.assertEqual(result,True)

        p1 = Post.objects.create(title='post1',text='Post1 text')
        UserObjectPermission.objects.create(user=self.testuser,can_change=True,subject=p1)
        response = self.client.get("/admin/object_permissions_testapp/post/%s/"%(p1.pk))
        self.assertEqual(response.status_code,200)

    def test_user_permission_changelist(self):
        result = self.client.login(username="testuser",password="testuser")
        self.assertEqual(result,True)

        p1 = Post.objects.create(title='post1',text='Post1 text')
        UserObjectPermission.objects.create(user=self.testuser,can_change=True,subject=p1)
        response = self.client.get("/admin/object_permissions_testapp/post/")
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"1 post")

    def test_group_permission_change(self):
        result = self.client.login(username="testuser",password="testuser")
        self.assertEqual(result,True)

        p1 = Post.objects.create(title='post1',text='Post1 text')
        GroupObjectPermission.objects.create(group=self.testgroup,can_change=True,subject=p1)
        self.testuser.groups.add(self.testgroup)
        response = self.client.get("/admin/object_permissions_testapp/post/%s/"%(p1.pk))
        self.assertEqual(response.status_code,200)

    def test_group_permission_changelist(self):
        result = self.client.login(username="testuser",password="testuser")
        self.assertEqual(result,True)

        p1 = Post.objects.create(title='post1',text='Post1 text')
        GroupObjectPermission.objects.create(group=self.testgroup,can_change=True,subject=p1)
        self.testuser.groups.add(self.testgroup)
        response = self.client.get("/admin/object_permissions_testapp/post/")
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"1 post")

    def test_auto_user_permission(self):
        result = self.client.login(username="testuser",password="testuser")
        self.assertEqual(result,True)

        response = self.client.post("/admin/object_permissions_testapp/post/add/",
            {'title':'post1','text':'Post1 text',#'_save':'Save',
            #'object_permissions-userobjectpermission-content_type-object_id-TOTAL_FORMS':0,
            #'object_permissions-userobjectpermission-content_type-object_id-INITIAL_FORMS':0,
            #'object_permissions-groupobjectpermission-content_type-object_id-TOTAL_FORMS':0,
            #'object_permissions-groupobjectpermission-content_type-object_id-INITIAL_FORMS':0,
            })
        self.assertEqual(Post.objects.count(),1)
        response = self.client.get("/admin/object_permissions_testapp/post/")
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"1 post")

    def test_auto_group_permission(self):
        result = self.client.login(username="testuser",password="testuser")
        self.assertEqual(result,True)

        response = self.client.post("/admin/object_permissions_testapp/post/add/",
            {'title':'post1','text':'Post1 text', })

        response = self.client.get("/admin/object_permissions_testapp/post/")
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"1 post")

        result = self.client.login(username="testuser2",password="testuser2")
        self.assertEqual(result,True)
        self.assertEqual(Post.objects.count(),1)

        response = self.client.get("/admin/object_permissions_testapp/post/")
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"0 posts")

        self.testuser2.groups.add(self.testgroup)
        response = self.client.get("/admin/object_permissions_testapp/post/")
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"1 post")

    def test_auto_permissions_create_only(self):
        result = self.client.login(username="testuser",password="testuser")
        self.assertEqual(result,True)

        response = self.client.post("/admin/object_permissions_testapp/post/add/",
            {'title':'post1','text':'Post1 text', })
        p1 = Post.objects.get(title='post1')

        self.assertEqual(UserObjectPermission.objects.filter(object_id=p1.id).count(),1)
        self.assertEqual(GroupObjectPermission.objects.filter(object_id=p1.id).count(),1)

        response = self.client.post("/admin/object_permissions_testapp/post/%s/"%(p1.pk),
                                {'title':'post1','text':'somenewtext'})

        self.assertEqual(UserObjectPermission.objects.filter(object_id=p1.id).count(),1)
        self.assertEqual(GroupObjectPermission.objects.filter(object_id=p1.id).count(),1)

    def test_change_all_permission(self):
        p1 = Post.objects.create(title='post1',text='Post1 text')
        p2 = Post.objects.create(title='post2',text='Post2 text')

        result = self.client.login(username="testuser",password="testuser")
        self.assertEqual(result,True)
        ct_type = ContentType.objects.get_for_model(Post)
        Permission.objects.get(name='Can change ALL post',content_type=ct_type).user_set.add(self.testuser)

        response = self.client.get("/admin/object_permissions_testapp/post/%s/"%(p1.pk))
        self.assertEqual(response.status_code,200)
        response = self.client.get("/admin/object_permissions_testapp/post/%s/"%(p2.pk))
        self.assertEqual(response.status_code,200)

