# TODO: Wrap blob functions in try excepts
from google.cloud import storage

class GCPStorage:
	def __init__(self, username):
		# https://cloud.google.com/storage/docs/creating-buckets#storage-create-bucket-code_samples
		self.storage_client = storage.Client()

		# Buckets are in a global namespace, so we will make them unique by using the format dropbucket-<username>
		self.bucket_name = "dropbucket-{}".format(username)

		if self.storage_client.lookup_bucket(self.bucket_name) == None:
			# Bucket for user doesn't exist so create one
			try:
				bucket = self.storage_client.create_bucket(self.bucket_name)
				self.gcp_bucket = self.storage_client.get_bucket(self.bucket_name)
				print('Bucket {} created'.format(bucket.name))
			except:
				print("Error occurred while trying to create a bucket")
		else:
			print('Bucket {} already exists'.format(self.bucket_name))
			self.gcp_bucket = self.storage_client.get_bucket(self.bucket_name)


	def upload(self, file):
		# https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-code-sample
		blob = self.gcp_bucket.blob(file.relative_path)

		# Upload temporary local file to bucket
		blob.upload_from_filename(file.relative_path)

		print('File {} uploaded to bucket {}'.format(file.relative_path, self.bucket_name))

		# TODO: Should we return a gcp url to the this uploaded file?

	def download(self, relative_path):
		# https://cloud.google.com/storage/docs/downloading-objects#storage-download-object-python
		blob = self.gcp_bucket.blob(relative_path)

		fileData = blob.download_as_string() # Do we need to write to a temporary file before streaming?

		print(fileData)

	def list(self):
		# https://cloud.google.com/storage/docs/listing-objects
		blobs = self.storage_client.list_blobs(self.bucket_name)

		for blob in blobs:
			print(blob.name)

	def delete(self, file):
		# https://cloud.google.com/storage/docs/deleting-objects
		blob = self.gcp_bucket.blob(file.relative_path)

		blob.delete()

		print('Blob {} deleted'.format(file.relative_path))


class File: # This is temporary
	def __init__(self, relative_path):
		self.relative_path = relative_path


# The data should be sent in binary
relative_path = "testDir/test.txt"
file = File(relative_path)

gcpStorage = GCPStorage("thomas"); # These names need to be unique
# gcpStorage.upload(file)
# gcpStorage.delete(file)
# gcpStorage.download(relative_path)
# gcpStorage.list()
# Let's say names are dropbucket-<username>
