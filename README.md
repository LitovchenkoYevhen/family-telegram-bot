# Family Telegram Bot

Телеграм-бот для учета семейных финансов. Позволяет отслеживать доходы и расходы, получать статистику и анализировать финансовые данные.

## Функциональность

- Добавление доходов и расходов
- Категоризация транзакций
- Получение статистики по периодам
- Визуализация данных
- Поддержка нескольких пользователей

## Технологии

- Python 3.11
- PostgreSQL
- SQLAlchemy
- Docker
- AWS (EC2, RDS, ECS)

## Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/family-telegram-bot.git
cd family-telegram-bot
```

2. Создайте файл `.env` и настройте переменные окружения:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=family_bot
POSTGRES_HOST=db
POSTGRES_PORT=5432
LOG_LEVEL=INFO
```

3. Запустите приложение с помощью Docker Compose:
```bash
docker-compose up -d
```

## Развертывание на AWS

### 1. Подготовка AWS инфраструктуры

#### Создание VPC
1. Создайте VPC с двумя публичными и двумя приватными подсетями
2. Настройте Internet Gateway для публичных подсетей
3. Создайте NAT Gateway для приватных подсетей
4. Настройте таблицы маршрутизации

#### Создание RDS
1. Создайте инстанс PostgreSQL в приватной подсети
2. Настройте Security Group для доступа из ECS
3. Создайте базу данных и пользователя
4. Сохраните параметры подключения

#### Создание ECS кластера
1. Создайте кластер ECS
2. Настройте Security Group для доступа к интернету
3. Создайте Task Definition для бота
4. Настройте Service для запуска бота

### 2. Настройка CI/CD

#### Создание ECR репозитория
```bash
aws ecr create-repository --repository-name family-telegram-bot
```

#### Настройка GitHub Actions
1. Создайте секреты в GitHub:
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - AWS_REGION
   - TELEGRAM_BOT_TOKEN
   - DB_HOST
   - DB_NAME
   - DB_USER
   - DB_PASSWORD

2. Создайте workflow файл `.github/workflows/deploy.yml`:
```yaml
name: Deploy to AWS

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: family-telegram-bot
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
      
      - name: Update ECS service
        run: |
          aws ecs update-service --cluster family-bot-cluster --service family-bot-service --force-new-deployment
```

### 3. Мониторинг и логирование

#### Настройка CloudWatch
1. Создайте группу логов
2. Настройте метрики для мониторинга
3. Создайте дашборды для визуализации

#### Настройка алертов
1. Создайте алерты для критических метрик
2. Настройте уведомления через SNS
3. Добавьте интеграцию с Telegram для уведомлений

## Структура проекта

```
family-telegram-bot/
├── src/
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── transaction.py
│   └── utils/
│       ├── __init__.py
│       ├── database.py
│       └── visualization.py
├── tests/
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Безопасность

- Все чувствительные данные хранятся в AWS Secrets Manager
- Используется шифрование данных в покое
- Настроены Security Groups для ограничения доступа
- Регулярное обновление зависимостей
- Мониторинг безопасности через AWS Security Hub

## Масштабирование

- Автоматическое масштабирование ECS сервиса
- Репликация базы данных
- Кэширование часто используемых данных
- Оптимизация запросов к базе данных

## Поддержка

При возникновении проблем:
1. Проверьте логи в CloudWatch
2. Убедитесь, что все сервисы работают
3. Проверьте настройки безопасности
4. Создайте issue в репозитории

## Лицензия

MIT
