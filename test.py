from couchbase.cluster import Cluster, ClusterOptions
from couchbase_core.cluster import PasswordAuthenticator

# needed to support SQL++ (N1QL) query
from couchbase.cluster import QueryOptions

# get a reference to our cluster
cluster = Cluster('couchbase://localhost', ClusterOptions(
  PasswordAuthenticator('Administrator', 'password')))
# get a reference to our bucket
cb = cluster.bucket('gamesim-sample')
# get a reference to the default collection
cb_coll = cb.default_collection()

ID_card = {
  "gender": "female",
  "id": 1234,
  "name": "sude",
  "surname": "celen",
}

def upsert_document(doc):
  print("\nUpsert CAS: ")
  try:
    key = doc["gender"] + "_" + str(doc["id"])
    result = cb_coll.upsert(key, doc)
    print(result.cas)
  except Exception as e:
    print(e)

upsert_document(ID_card)


def ID_Card_by_key(key):
  print("\nGet Result: ")
  try:
    result = cb_coll.get(key)
    print(result.content_as[str])
  except Exception as e:
    print(e)
	
upsert_document(ID_card)



def deneme(cs):
  print("\nLookup Result: ")
  try:
    sql_query = 'SELECT VALUE id FROM `gamesim-sample` WHERE gender = "female" AND name = $1'
    row_iter = cluster.query(
      sql_query,
      QueryOptions(positional_parameters=[cs]))
    for row in row_iter: print(row)
  except Exception as e:
    print(e)

deneme("1234")
