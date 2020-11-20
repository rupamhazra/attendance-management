from django.contrib import admin

from master.models import *

@admin.register(AccessPermission)
class AccessPermission(admin.ModelAdmin):
    list_display = [field.name for field in AccessPermission._meta.fields]

@admin.register(Module)
class Module(admin.ModelAdmin):
    list_display = [field.name for field in Module._meta.fields]

@admin.register(Other)
class Other(admin.ModelAdmin):
    list_display = [field.name for field in Other._meta.fields]
    search_fields = ('cot_name',)

# @admin.register(Role)
# class Role(admin.ModelAdmin):
#     list_display = [field.name for field in Role._meta.fields]

@admin.register(Department)
class Department(admin.ModelAdmin):
    list_display = [field.name for field in Department._meta.fields]

@admin.register(Designation)
class Designation(admin.ModelAdmin):
    list_display = [field.name for field in Designation._meta.fields]
    search_fields = ('cod_name',)

@admin.register(Company)
class Company(admin.ModelAdmin):
    list_display = [field.name for field in Company._meta.fields]

@admin.register(Grade)
class Grade(admin.ModelAdmin):
    list_display = [field.name for field in Grade._meta.fields]
    search_fields = ('cg_name',)

@admin.register(Category)
class Category(admin.ModelAdmin):
    list_display = [field.name for field in Category._meta.fields]
    search_fields = ('name',)

@admin.register(ModuleUser)
class ModuleUser(admin.ModelAdmin):
    list_display = [field.name for field in ModuleUser._meta.fields]
    search_fields = ('mmr_module__cm_name', 'mmr_user__username','mmr_role__cr_name')

@admin.register(ModuleOther)
class ModuleOther(admin.ModelAdmin):
    list_display = [field.name for field in ModuleOther._meta.fields]

# @admin.register(OtherRole)
# class OtherRole(admin.ModelAdmin):
#     list_display = [field.name for field in OtherRole._meta.fields]
#     search_fields = ('mor_role__id',)

@admin.register(OtherUser)
class OtherUser(admin.ModelAdmin):
    list_display = [field.name for field in OtherUser._meta.fields]
    search_fields = ('mou_user__id',)

@admin.register(TemplateMaster)
class TemplateMaster(admin.ModelAdmin):
    list_display = [field.name for field in TemplateMaster._meta.fields]
    search_fields = ('template_name',)

# @admin.register(ModuleRole)
# class ModuleRole(admin.ModelAdmin):
#     list_display = [field.name for field in ModuleRole._meta.fields]
#     search_fields = ('mmro_module__id',)



