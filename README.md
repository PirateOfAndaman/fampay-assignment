# FamPay Video Search API

A Django application with Celery for managing and searching video content.

## 🚀 Features

- Video content management and storage
- Full-text search functionality
- Automated fetching of latest videos via Celery tasks
- RESTful API for video search
- Dockerized deployment

## 🫠️ Tech Stack

- Django 5.1.x
- Celery for background task processing
- SQLite for database 
- Redis for Celery message broker
- Full-text search with SQLite FTS
- Docker & Docker Compose for containerization

## 👋 Prerequisites

- Docker and Docker Compose
- Git

## 🔧 Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fampay.git
   cd fampay
   ```
2. Add a .credentials file in the root directory of project
    ```bash
    YOUTUBE_API_KEYS=KEY1,KEY2
    ```
3. Make Migrations
  python manage.py migrate
  python manage.py migrate video

4. Start Celery worker
  ```bash
  celery -A fampay worker --loglevel=info &
  ```
5. Start Celery beat
  ```bash
  celery -A fampay beat --loglevel=info &
  ```

6. The application will be available at:
   - Django server: [http://localhost:8000](http://localhost:8000)
   - API endpoints: [http://localhost:8000/api/](http://localhost:8000/api/)

## Or Just User Docker 
Build your image with, make sure you have added the .credentials file

```bash
docker compose up
```

## 📚 API Documentation

### Search API

The application provides a powerful search API for finding videos based on text queries.

#### Endpoint

```
GET /api/search/
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| q | string | **Required**. The search query text |
| page | integer | Page number for pagination (default: 1) |
| page_size | integer | Number of results per page (default: 10) |

#### Example Request

```bash
curl "http://localhost:8000/api/search/?q=official&page=1&page_size=20"
```

#### Response

```json
{
  "count": 42,
  "total_pages": 3,
  "current_page": 1,
  "results": [
    {
      "id": 123,
      "title": "Official Example Video",
      "description": "This is an example video description",
      "thumbnail_url": "https://example.com/thumbnail.jpg",
      "published_at": "2025-03-21T00:00:00Z",
      "channel_title": "Example Channel"
    }
  ]
}
```

#### Error Responses

- **400 Bad Request**: Missing required query parameter
  ```json
  {"error": "Query parameter 'q' is required."}
  ```

- **500 Internal Server Error**: Database or server error
  ```json
  {"error": "Internal server error"}
  ```

## 🔄 Automated Tasks

The application includes automated Celery tasks:

- `fetch_latest_videos`: Periodically fetches the newest videos
- `fetch_videos_for_query`: Fetches videos for specific search queries

## 💂️ Project Structure

```
/fampay
│── /fampay                   # Django project
│── /apps
│   └── /video                # Django app for videos
│── Dockerfile                # Docker instructions
│── docker-compose.yml        # Container orchestration
│── entrypoint.sh             # Script to initialize Django app
│── requirements.txt          # Python dependencies
│── manage.py                 # Django management script
│── .credentials              # User has to provide youtube api keys
```
