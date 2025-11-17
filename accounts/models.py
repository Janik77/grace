from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Department(models.Model):
    """Отдел компании (Дизайн, Цех, Офис и т.д.)"""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"

    def __str__(self):
        return self.name


class Position(models.Model):
    """Должность сотрудника"""
    name = models.CharField(max_length=120, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="positions"
    )

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"

    def __str__(self):
        return self.name


class Skill(models.Model):
    """Навык (печать, резка, сборка и т.д.)"""
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=120)

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Основная модель сотрудника"""
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_profile"
    )
    full_name = models.CharField("ФИО", max_length=200, db_index=True)
    phone = models.CharField("Телефон", max_length=32, blank=True)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    status = models.CharField("Статус", max_length=20, default="штатно работает")
    main_position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees"
    )
    skills = models.ManyToManyField(
        Skill,
        through="EmployeeSkill",
        related_name="employees"
    )

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.full_name


class EmployeeSkill(models.Model):
    """Связь сотрудника с навыком (многие ко многим)"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    is_primary = models.BooleanField("Основной навык", default=False)
    started_at = models.DateField("Дата начала", null=True, blank=True)
    note = models.CharField("Комментарий", max_length=200, blank=True)

    class Meta:
        unique_together = ("employee", "skill")
        verbose_name = "Навык сотрудника"
        verbose_name_plural = "Навыки сотрудников"

    def __str__(self):
        return f"{self.employee.full_name} - {self.skill.name}"
