.PHONY: setup up down logs clean

setup: 
    @echo "Setting up local environment..."
    @if [ ! -f .env ]; then cp .env.example .env; echo ".env created from .env.example"; fi
    @echo "Setup complete. Run 'make up' to start the project."

up:
    docker-compose up --build

down:
    docker-compose down

logs:
    docker-compose logs -f

clean:
    docker-compose down -v
    @echo "Containers and volumes removed."