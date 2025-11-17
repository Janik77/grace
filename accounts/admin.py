from django.contrib import admin
from .models import Department, Position, Skill, Employee, EmployeeSkill


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("name", "department")
    list_filter = ("department",)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


class EmployeeSkillInline(admin.TabularInline):
    model = EmployeeSkill
    extra = 1


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "main_position", "status")
    search_fields = ("full_name", "phone")
    list_filter = ("main_position", "status")
    inlines = [EmployeeSkillInline]
