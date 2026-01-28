# Photo Classification Platform









A minimal microservices-based platform for user photo submissions and admin review.









## Services




- **api**: FastAPI app for auth, submissions, admin panel, storage integration.




- **classifier**: FastAPI service that returns a deterministic classification label.




- **db**: Postgres 15 for metadata storage.









## Local run (Docker)




```bash




docker compose up --build




```









API docs: `http://localhost:8000/docs`









Admin panel: `http://localhost:8000/admin`









### Default admin




Configured via environment variables:




- `ADMIN_EMAIL=admin@photoclassify.com`




- `ADMIN_PASSWORD=admin123`









### Database migrations




```bash




docker compose exec api alembic -c /app/alembic.ini upgrade head




```









## Core API




- `POST /auth/register`




- `POST /auth/login`




- `POST /submissions` (multipart: photo + metadata)




- `GET /submissions/{id}`




- `GET /admin/submissions` (filters: age_min, age_max, gender, place_of_living, country_of_origin)




- `GET /admin` (HTML table)









## Database choice and schema




Postgres is used for relational metadata with indexing and filtering. It provides strong schema guarantees and is the most common fit for analytics-friendly querying.









Tables:




- `users`: login, admin flag




- `submissions`: metadata + photo path + classification + timestamps




- `audit_logs`: lightweight tracking for key user actions









Indexes:




- `users.email` (unique)




- `submissions.age`, `submissions.gender`, `submissions.place_of_living`, `submissions.country_of_origin`




- `submissions.user_id`, `audit_logs.user_id`









Migrations live in `services/api/alembic`.









## Storage layer




Photos are stored on the API container volume at `/data/photos` and the path is stored in Postgres. This keeps metadata and blobs separate and makes it easy to swap in object storage later (e.g., S3/MinIO).









## Safety rules




Implemented in `services/api/app/storage.py` and `services/api/app/auth.py`.




- **File size limit**: `MAX_UPLOAD_BYTES` (default 5MB). Prevents large uploads from exhausting disk.




- **Content-type allowlist**: only JPEG/PNG. Reduces attack surface.




- **JWT-based auth**: protects endpoints and admin-only routes.




- **Admin-only access**: enforced via token claims and DB role flags.









## Security




- Password hashing with bcrypt




- JWT tokens with expiration




- Database credentials provided via environment variables









## Kubernetes strategy




Manifests are in `infra/k8s`:




- Deployments for `api` and `classifier`




- Postgres stateful set (or use managed DB in production)




- Services for internal routing




- Ingress for public access









Scaling and observability:




- Scale `classifier` independently from `api`.




- Configure HPA on CPU/memory; add request-based autoscaling if using KEDA.




- Use Kubernetes secrets for JWT and DB credentials.




- Add OpenTelemetry sidecars or FastAPI instrumentation for traces.









## CI/CD




GitHub Actions workflow in `.github/workflows/ci.yml`:




- Lint with `ruff`




- Run tests with `pytest`




- Build Docker images for `api` and `classifier`




- Optional push step to a container registry (requires secrets)




- Optional deploy step using `kubectl` and a kubeconfig secret









## Architecture diagram




`docs/architecture.drawio` provides a block diagram for draw.io.




