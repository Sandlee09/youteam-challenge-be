from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy import create_engine, inspect, MetaData, Table, text
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy.exc import SQLAlchemyError
from models import Base, ColumnRelationship
from typing import List, Dict

app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up the database connection
engine = create_engine("postgresql://postgres:Gabriel09@localhost/TurnTable")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


#GET DATABASE SESSION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#2 HEALTH CHECK
@app.get("/", response_model=dict, status_code=200)
def health_check():
    return {"message": "OK"}


#3 GET TABLE STATS
@app.get("/tables/stats", response_model=dict, status_code=200)
def get_warehouse_stats(db=Depends(get_db)):
    inspector = inspect(db.get_bind())
    tables = inspector.get_table_names()
    total_columns = 0
    documented_columns = 0

    for table_name in tables:
        table = Base.metadata.tables[table_name]
        total_columns += len(table.columns)
        for column in table.columns:
            if column.doc:
                documented_columns += 1

    return {
        "tables": len(tables),
        "columns": total_columns,
        "documented_columns": documented_columns
    }





#3 PATCH endpoint to update column descriptions START
def snake_case(name):
    name_with_underscores = ''.join(['_'+i.lower() if i.isupper() else i for i in name]).lstrip('_')
    return name_with_underscores

def find_select_relationships_by_source(tablename, columnname):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        # Capitalize the tablename
        capitalized_tablename = tablename.capitalize()
        
        # Construct the SQL query using SQLAlchemy's text() construct
        query = text("SELECT * FROM column_relationships WHERE source=:source AND type='select'")
        
        # Execute the query with the capitalized tablename.columnname as the source parameter
        result = session.execute(query, {"source": f"{capitalized_tablename}.{columnname}"})
        
        # Fetch all rows from the result
        rows = result.fetchall()
        return rows
    finally:
        session.close()


def update_column_description(table_name: str, column_name: str, description: str, db):
    try:
        select_relationships = find_select_relationships_by_source(table_name, column_name)
        
        #Update all Relationships
        for relationship in select_relationships:
            relationship_tablename, relationship_column = relationship.target.split(".")
            relationship_tablename = snake_case(relationship_tablename)
            query = text(f"COMMENT ON COLUMN {relationship_tablename}.\"{relationship_column}\" IS '{description}'")
            db.execute(query)

        query = text(f"COMMENT ON COLUMN {table_name}.\"{column_name}\" IS '{description}'")
        db.execute(query)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/tables/{table_name}")
async def edit_table_columns(
    table_name: str, column_data: Dict[str, Dict[str, str]], db: Session = Depends(get_db)
):
    for column_name, update_data in column_data.items():
       update_column_description(table_name, column_name, update_data.get("description"), db)


    return {"message": "Columns updated successfully"}
#3 PATCH endpoint to update column descriptions END



#GET ALL TABLE RELATIONSHIPS
@app.get("/tables/relationships/{table_name}", response_model=list[Dict])
def get_all_relationships(table_name: str, db=Depends(get_db)):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    # GET ALL BASE RELATIONSHIPS
    current_tablename = snake_case(table_name)
    query = text(f"SELECT * FROM {current_tablename}")
    result_current_table = session.execute(query)
    current_rows = result_current_table.fetchall()
    current_table = [dict(row) for row in current_rows]
    print(result_current_table)

    # GET ALL BASE RELATIONSHIPS
    lowercase_tablename = table_name.lower()
    query = text("SELECT * FROM column_relationships WHERE source ILIKE :source")
    result = session.execute(query, {"source": "%"+lowercase_tablename+"%"})
    rows = result.fetchall()
    first_relationship_data = []
    for row in rows:
        dictionary_row = {
            "id": row[0],
            "source": row[1],
            "target": row[2],
            "join_type": row[3]
        }
        first_relationship_data.append(dictionary_row)


    # Extract table names from the source column of each row
    table_names = [relationship['target'].split('.')[0] for relationship in first_relationship_data]
    
    # Create a dictionary to store table names and their columns
    table_columns = {}

    # Query the database schema to retrieve columns for each table
    for table_name in set(table_names):  # Using set to ensure unique table names
        table_name = snake_case(table_name)
        columns_query = text(f"SELECT column_name FROM information_schema.columns WHERE table_name = :table_name")
        columns_result = session.execute(columns_query, {"table_name": table_name})

        columns = [row[0] for row in columns_result.fetchall()]
        table_columns[table_name] = columns

    # Add the columns information to the second_relationships_data
    relationships_data = []
    for relationship in first_relationship_data:
        source_table = relationship['target'].split('.')[0]
        source_table = snake_case(source_table)
        source_columns = table_columns.get(source_table, [])
        relationship_dict = dict(relationship)
        relationship_dict['source_columns'] = source_columns
        relationships_data.append(relationship_dict)

    session.close()
    
    return relationships_data



#GET ALL TABLES
@app.get("/tables", response_model=List[Dict])
def get_all_tables(db=Depends(get_db)):
    inspector = inspect(db.get_bind())
    table_info = []

    for table_name in inspector.get_table_names():
        table_columns = inspector.get_columns(table_name)
        table_dict = {
            "name": table_name,
            "columns": []
        }

        for column in table_columns:
            column_dict = {
                "name": column["name"],
                "type": column["type"].__class__.__name__,
                "description": column.get("comment", "")
            }
            table_dict["columns"].append(column_dict)

        table_info.append(table_dict)

    return table_info



# Insert provided data into the column_relationships table
data = [
    {"source": "Orders.CustomerID", "target": "Customers.CustomerID", "type": "join"},
    {"source": "OrderDetails.OrderID", "target": "Orders.OrderID", "type": "join"},
    {"source": "OrderDetails.ProductID", "target": "Products.ProductID", "type": "join"},
    {"source": "Products.CategoryID", "target": "Categories.CategoryID", "type": "join"},
    {"source": "Reviews.ProductID", "target": "Products.ProductID", "type": "join"},
    {"source": "Shipping.OrderID", "target": "Orders.OrderID", "type": "join"},
    {"source": "Payments.OrderID", "target": "Orders.OrderID", "type": "join"},
    {"source": "Products.Price", "target": "OrderDetails.UnitPrice", "type": "select"},
    {"source": "Customers.Country", "target": "Orders.ShippingAddress", "type": "filter"},
    {"source": "Inventory.QuantityAvailable", "target": "Products.StockQuantity", "type": "filter"},
    {"source": "Reviews.Rating", "target": "Products.ProductID", "type": "group"},
    {"source": "Orders.TotalAmount", "target": "OrderDetails.Amount", "type": "select"},
    {"source": "OrderDetails.Amount", "target": "Payments.Amount", "type": "select"}
]

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_relationships():
    session = SessionLocal()
    try:
        for item in data:
            session.add(ColumnRelationship(**item))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# Call the function to create and insert data into the column_relationships table
# create_relationships()