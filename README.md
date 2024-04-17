HOW TO SETUP BE:

1. Download anaconda
2. Create venv :conda create --name resortSync
3. Switch to venv: conda activate resortSync
4. List all installed packages : pip freeze > uninstallPackages.txt
5. Uninstall all packages: pip uninstall -r uninstallPackages.txt -y
6. install dependencies: pip install -r requirements.txt
7. Create database ResortSyncDB in postgres DB
8. Run uvicorn main:app --reload

Running migrations is necessary when you make changes to the structure of your database, such as creating, modifying, or deleting tables and columns. Migrations help keep your database schema in sync with your application code as it evolves over time.

to run a migration run

//Create and Run Migration
alembic revision --autogenerate -m "commit message"
alembic upgrade head

//TO RERUN MIGRATION
alembic downgrade -1
alembic upgrade head


//Return Migrations to Base
alembic downgrade base

//Start Server
uvicorn main:app --reload

//Swagger
http://127.0.0.1:8000/docs