from pytm import TM, Server, Datastore, Dataflow, Actor, Boundary

tm = TM("Task Management System")
tm.description = "A FastAPI application with SQLAlchemy and PostgreSQL"

# Define Entities
user = Actor("Employee")
api = Server("FastAPI Backend")
db = Datastore("PostgreSQL (SQLAlchemy)")

# Define Boundaries
internet = Boundary("Public Internet")
cloud = Boundary("Private Cloud")

user.inBoundary = internet
api.inBoundary = cloud
db.inBoundary = cloud

# Define Flows
Dataflow(user, api, "Sends Task Data (JSON)")
Dataflow(api, db, "SQL Query (CRUD)")

tm.process()
