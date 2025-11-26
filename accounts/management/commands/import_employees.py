import os

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand

from accounts.models import Department, Employee, EmployeeSkill, Position, Skill


class Command(BaseCommand):
    help = "Импорт сотрудников из Excel с отделами, должностями и навыками"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help=(
                "Путь к Excel-файлу (например: C\\Users\\user\\Downloads\\employees.xlsx). "
                "Если не указан, будет использован data/employees.xlsx внутри проекта."
            ),
        )

    def handle(self, *args, **options):
        provided_path = options.get("file")
        default_path = os.path.join(settings.BASE_DIR, "data", "employees.xlsx")
        file_path = provided_path or default_path

        if not os.path.exists(file_path):
            error_msg = f"Файл не найден: {file_path}"
            if not provided_path:
                error_msg += " (укажите путь через --file, если файл лежит в другом месте)"
            self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))
            return

        df = pd.read_excel(file_path)
        self.stdout.write(self.style.WARNING(f"📂 Импорт начат из файла: {file_path}"))

        total = 0

        for _, row in df.iterrows():
            fio = row.get('ФИО')
            if not fio or pd.isna(fio):
                continue

            phone = str(row.get('Телефон')) if pd.notna(row.get('Телефон')) else None
            status = row.get('Статус', 'штатно работает')
            birth_date = row.get('Дата рождения') or row.get('Дата', None)
            dept_name = row.get('Отдел')
            position_name = row.get('Должность')
            skills_str = row.get('Навыки', '')

            # === Отдел ===
            department = None
            if pd.notna(dept_name) and str(dept_name).strip():
                department, _ = Department.objects.get_or_create(name=str(dept_name).strip())

            # === Должность ===
            position = None
            if pd.notna(position_name) and str(position_name).strip():
                position, _ = Position.objects.get_or_create(
                    name=str(position_name).strip(),
                    defaults={"department": department}
                )
                if department and position.department != department:
                    position.department = department
                    position.save()

            # === Сотрудник ===
            employee, _ = Employee.objects.update_or_create(
                full_name=fio.strip(),
                defaults={
                    "phone": phone,
                    "status": status,
                    "birth_date": birth_date,
                    "main_position": position,
                }
            )

            # === Навыки ===
            if pd.notna(skills_str) and skills_str.strip():
                skill_names = [s.strip() for s in str(skills_str).split(',')]
                for skill_name in skill_names:
                    skill_obj, _ = Skill.objects.get_or_create(
                        name=skill_name,
                        defaults={"code": skill_name.lower().replace(" ", "_")}
                    )
                    EmployeeSkill.objects.get_or_create(
                        employee=employee,
                        skill=skill_obj,
                        defaults={"is_primary": False}
                    )

            total += 1
            self.stdout.write(self.style.SUCCESS(f"✅ {fio} импортирован"))

        self.stdout.write(self.style.SUCCESS(f"\nИмпорт завершён успешно. Добавлено/обновлено {total} сотрудников ✅"))
