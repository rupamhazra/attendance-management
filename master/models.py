from django.db import models
#from django.contrib.auth.models import User
import collections
from datetime import datetime
from dynamic_media import get_directory_path
from django.conf import settings

class CustomManager(models.Manager):
    def get_queryset(self):
        return super(__class__, self).get_queryset().filter(is_deleted=False)

class DeleteBaseAbstractStructure(models.Model):
    is_deleted = models.BooleanField(default=False)

    objects = models.Manager()
    cmobjects = CustomManager()
    class Meta:
        abstract = True
    
class CreateBaseAbstractStructure(DeleteBaseAbstractStructure):
    created_at = models.DateTimeField(default=datetime.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    class Meta:
        abstract = True 

class UpdateBaseAbstractStructure(CreateBaseAbstractStructure):
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

class BaseAbstractStructure(UpdateBaseAbstractStructure):
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    # def save(self, *args, **kwargs):
    #     self.updated_at = datetime.now()
    #     super(__class__, self).save(*args, **kwargs)


class AccessPermission(BaseAbstractStructure):
    name = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'access_permission'

    def __str__(self):
        return str(self.id)


# class Role(models.Model):
#     name = models.CharField(max_length=100, blank=True, null=True)
#     parent_id = models.IntegerField(default=0)
#     is_deleted = models.BooleanField(default=False)
#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='r_created_by', blank=True, null=True)
#     created_at = models.DateTimeField(default=datetime.now)
#     updated_at = models.DateTimeField(blank=True, null=True)
#     updated_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='r_updated_by', blank=True, null=True)
#     deleted_at = models.DateTimeField(blank=True, null=True)
#     deleted_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='r_deleted_by', blank=True, null=True)

#     def __str__(self):
#         return str(self.id)

#     class Meta:
#         db_table = 'roles'


class Module(BaseAbstractStructure):
    # permission_type = (
    #     (1, 'Public Read/Write'),
    #     (2, 'Public Read Only'),
    #     (3, 'Private')
    # )
    name = models.CharField(max_length=100, blank=True, null=True, unique=True)
    desc = models.TextField(blank=True, null=True)
    icon = models.ImageField(upload_to=get_directory_path,
                             default=None, blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    is_editable = models.BooleanField(default=True)
    
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'modules'


class Other(BaseAbstractStructure):
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    parent_id = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'others'


class Company(BaseAbstractStructure):
    name = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    short_name = models.CharField(max_length=50, blank=True, null=True)
    email_id_1 = models.CharField(max_length=100, blank=True, null=True)
    email_id_2 = models.CharField(max_length=100, blank=True, null=True)
    total_no_gate_pass = models.IntegerField(blank=True, null=True)
    gate_pass_monthly_duration = models.FloatField(blank=True, null=True)
    
    def __str__(self):
        return str(self.id)

    def get_name(self):
        return str(self.name)

    class Meta:
        db_table = 'company'
        

    # def save(self,*args, **kwargs):
    #     updated = False
    #     #print('force_insert',force_insert)
    #     if not self.pk: # insert method
    #         updated = AccessPermission.objects.create(name='Read')
    #     if self.pk: # update method
    #         print('self.pk',self.pk)
    #         print('update')
    #         updated = AccessPermission.objects.create(name='Write')
    #         pass
    #         #updated = AccessPermission.objects.create(name='Read')
    #     return super().save(*args, **kwargs)


class Category(BaseAbstractStructure):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='cat_company', blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return str(self.id)

    def get_name(self):
        return str(self.name)

    class Meta:
        db_table = 'category'


class Department(BaseAbstractStructure):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='d_category', blank=True, null=True)
    code = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    hod = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            related_name='d_hod', blank=True, null=True)
    parent = models.IntegerField(default=0, blank=True, null=True)
    
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'department'


class Designation(BaseAbstractStructure):
    name = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'designation'


class Grade(BaseAbstractStructure):
    code = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    parent = models.IntegerField(default=0, blank=True, null=True)
    no_of_mispunch_or_manual = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'grade'

# Mapping Tables


# class ModuleRole(models.Model):
#     mmro_module = models.ForeignKey(
#         Module, on_delete=models.CASCADE, related_name='mmr_o_module')
#     mmro_role = models.ForeignKey(
#         Role, on_delete=models.CASCADE, related_name='mmr_o_role', blank=True, null=True,)
#     mmro_is_deleted = models.BooleanField(default=False)
#     mmro_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='mmr_o_created_by',
#                                         on_delete=models.CASCADE, blank=True, null=True)
#     mmro_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='mmr_o_updated_by',
#                                         on_delete=models.CASCADE, blank=True, null=True)
#     mmro_created_at = models.DateTimeField(default=datetime.now)
#     mmro_updated_at = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         db_table = 'module_role'

#     def __str__(self):
#         return str(self.id)


class ModuleOther(DeleteBaseAbstractStructure):
    mmo_other = models.ForeignKey(
        Other, on_delete=models.CASCADE, related_name='mmo_other')
    mmo_module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name='mmo_module')
    

    class Meta:
        db_table = 'module_other'

    def __str__(self):
        return str(self.id)


class ModuleUser(DeleteBaseAbstractStructure):
    TYPE_CHOICE = (
        (1, 'Super User'),
        (2, 'Module Admin'),
        (3, 'Module User'),
        (4, 'Dealer'),
        (5, 'CWS'),
        (6, 'Demo User')
    )

    mmr_module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name='mmr_module')
    # mmr_role = models.ForeignKey(
    #     Role, on_delete=models.CASCADE, related_name='mmr_role', blank=True, null=True,)
    mmr_type = models.IntegerField(
        default=1, choices=TYPE_CHOICE, blank=True, null=True,)
    mmr_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mmr_user', blank=True, null=True)
    

    class Meta:
        db_table = 'module_user'

    def __str__(self):
        return str(self.id)


# class OtherRole(models.Model):
#     """
#         Used for assigning object permisson to role
#     """
#     mor_role = models.ForeignKey(
#         Role, on_delete=models.CASCADE, related_name='mor_r_role', blank=True, null=True)
#     mor_other = models.ForeignKey(
#         Other, on_delete=models.CASCADE, related_name='mor_r_other')
#     mor_permissions = models.ForeignKey(Permission, on_delete=models.CASCADE,
#                                         related_name='mor_permissions', blank=True, null=True)
#     mor_module = models.ForeignKey(
#         Module, on_delete=models.CASCADE, related_name='mor_module')
#     mor_is_deleted = models.BooleanField(default=False)
#     mor_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mor_r_created_by', blank=True,
#                                        null=True)
#     mor_created_at = models.DateTimeField(default=datetime.now)
#     mor_updated_at = models.DateTimeField(blank=True, null=True)
#     mor_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mor_r_updated_by', blank=True,
#                                        null=True)
#     mor_deleted_at = models.DateTimeField(blank=True, null=True)
#     mor_deleted_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mor_r_deleted_by', blank=True, null=True)

#     class Meta:
#         db_table = 'other_role'

#     def __str__(self):
#         return str(self.id)


class OtherUser(BaseAbstractStructure):
    """
        Used for assigning object permisson to user
    """
    mou_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mou_r_user', blank=True, null=True)
    mou_other = models.ForeignKey(
        Other, on_delete=models.CASCADE, related_name='mou_r_other')
    mou_permissions = models.ForeignKey(AccessPermission, on_delete=models.CASCADE,
                                        related_name='mmr_permissions', blank=True, null=True)
    mou_module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name='mou_module')
    
    class Meta:
        db_table = 'other_user'

    def __str__(self):
        return str(self.id)

class TemplateMaster(DeleteBaseAbstractStructure):
    template_name = models.CharField(max_length=100, unique=True)
    subject = models.TextField()
    body = models.TextField()
    image_url = models.TextField(null=True, blank=True, default=None)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'template_master'

    def __str__(self):
        return str(self.id)
