# Data directory

Place your local Excel files here when running import commands. Expected filenames:

- `employees.xlsx` — сотрудники: ФИО, телефон, статус, отдел, должность, навыки
- `inventory.xlsx` — справочник товаров/материалов
- `materials.xlsx` — списания материалов со склада

Эти файлы не хранятся в репозитории и игнорируются `.gitignore`, чтобы избежать проблем с бинарными вложениями. Перед запуском команд импорта убедитесь, что нужные файлы лежат в этой папке или укажите путь через флаг `--file`.
