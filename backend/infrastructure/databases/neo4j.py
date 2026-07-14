from neo4j import GraphDatabase
from config.settings import settings

"""
Class that manages the Neo4j database.
"""
class Neo4j_DB:
  """
  Constructor for the Neo4j manager object
  """
  def __init__(self):
    # Load Neo4j credentials from environment variables
    self.NEO4J_URI = settings.NEO_CONNECTION_URL
    self.NEO4J_USERNAME = settings.NEO_DB_ID
    self.NEO4J_PASSWORD = settings.NEO_PASSWORD

    # Ensure credentials are set
    if not all([self.NEO4J_URI, self.NEO4J_USERNAME, self.NEO4J_PASSWORD]):
        raise ValueError("Neo4j credentials (NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD) must be set in environment variables or Colab secrets.")

  """
  Returns a driver for the Neo4j database
  """
  def get_driver(self):
    return GraphDatabase.driver(self.NEO4J_URI, auth=(self.NEO4J_USERNAME, self.NEO4J_PASSWORD))

  """
  Clears the database of all data before writing. I would have preferred to drop and create a database, but unforutnately such executive commands
  are not allowed for this sdk.
  """
  def clear_database(self):
    with self.driver.session() as session:
      session.run("MATCH (n) DETACH DELETE n", db="recommendations")

  """
  Helper method to write the frequent itemsets to Neo4j.
  params: tx (transaction)
          itemsets (list[set]) -- list of frequent itemsets
  """
  @staticmethod
  def write_frequent_itemsets_to_neo4j(tx, itemsets):
      # Create nodes for all items and relationships for each itemset
      for itemset in itemsets:
          item_names = list(itemset)
          if len(item_names) == 1:
              # For single items, just create the node
              item_name = item_names[0]
              tx.run("MERGE (i:Item {name: $item_name});", item_name=item_name)
          else:
              # For itemsets with multiple items, create nodes and connect them efficiently
              tx.run(
                  "UNWIND $item_names AS item1_name \n"
                  "UNWIND $item_names AS item2_name \n"
                  "WITH item1_name, item2_name \n"
                  "WHERE item1_name < item2_name // Ensure unique pairs and avoid self-loops \n"
                  "MERGE (i1:Item {name: item1_name}) \n"
                  "MERGE (i2:Item {name: item2_name}) \n"
                  "MERGE (i1)-[:ASSOCIATE]-(i2)",
                  item_names=item_names
              )

  """
  Writes the datasets to Neo4j
  """
  def update_database(self, itemsets):
    self.driver = self.get_driver()
    self.clear_database()

    with self.driver.session() as session:
      session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (i:Item) REQUIRE i.name IS UNIQUE;")
      session.execute_write(self.write_frequent_itemsets_to_neo4j, itemsets)

    self.driver.close()