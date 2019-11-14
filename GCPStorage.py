from google.cloud import storage

storage_client = storage.Client();

print(storage_client)

class GCPStorage:
	def __init__(self, username):
		self.storage_client = storage.Client()

		# Buckets are in a global namespace, so we will make them unique by using the format dropbucket-<username>
		self.bucket_name = "dropbucket-{}".format(username)

		if storage_client.lookup_bucket(self.bucket_name) == None:
			# Bucket for user doesn't exist so create one
			try:
				bucket = storage_client.create_bucket(self.bucket_name)
				print('Bucket {} created'.format(bucket.name))
			except:
				print("Error occurred while trying to create a bucket")
		else:
			print('Bucket {} already exists'.format(self.bucket_name))


GCPStorage("testbucketjuan"); # These names need to be unique
# Let's say names are dropbucket-<username>
