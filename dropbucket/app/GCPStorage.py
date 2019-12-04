# TODO: Change prints to use a logger
from google.cloud import storage
from hashlib import md5
import os

TEMP_DIR = "cache"

class GCPStorage:
	def __init__(self, username):
		"""
		Source: https://cloud.google.com/storage/docs/creating-buckets#storage-create-bucket-code_samples
		Takes in a username and creates a GCP bucket if one doesn't already exist.
		Bucket naming format is `dropbucket-<username>`

		Args:
			username (str): Username of current logged in account
		"""
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


	def upload(self, relative_path):
		"""
		Source: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-code-sample
		Takes in a file object and uploads it to the user's GCP bucket.

		Args:
			file (File): File object

		Returns:
			bool: The return value. True for success, False otherwise.
		"""
		# try:
		blob = self.gcp_bucket.blob(relative_path)

		# Upload temporary local file to bucket
		blob.upload_from_filename(relative_path)

		print('File {} uploaded to bucket {}'.format(relative_path, self.bucket_name))

		return True
		# except:
		# 	return False

	def download(self, file):
		"""
		TODO: Is there a way to just stream this and forward the results?
		Source: https://cloud.google.com/storage/docs/downloading-objects#storage-download-object-python
		Takes in a file object and uses the information in it to download a file from the user's GCP bucket

		Args:
			file (File): File object

		Returns:
			string: Path to a the file locally (we will download it to a temporary file)
		"""
		try:
			blob = self.gcp_bucket.blob(file.relative_path)

			# Check if temp folder exists, if not create it
			if not os.path.exists(TEMP_DIR):
				os.makedirs(TEMP_DIR)

			# Create a hash of the bucket_name + relative_path to use as a temporary filename
			filename = md5(bytes(self.bucket_name + file.relative_path, "utf-8")).hexdigest()
			pathToFile = "{}/{}".format(TEMP_DIR, filename)
			fp = open(pathToFile, "wb+")
			fileData = blob.download_to_file(fp)

			return pathToFile
		except:
			return ""

	def list(self):
		"""
		Source: https://cloud.google.com/storage/docs/listing-objects
		Returns a list of files contained in the user's bucket

		Args:

		Returns:
			list: The return value. A list of files (relative paths included) contained in the bucket.
		"""
		try:
			blobs = self.storage_client.list_blobs(self.bucket_name)
			return [blob.name for blob in blobs]
		except:
			return []

	def delete(self, file):
		"""
		Source: https://cloud.google.com/storage/docs/deleting-objects
		Takes in a file object and uses the information in it to download a file from the user's GCP bucket

		Args:
			file: File object

		Returns:
			bool: The return value. True for success, False otherwise.
		"""
		try:
			blob = self.gcp_bucket.blob(file.relative_path)

			blob.delete()

			print('Blob {} deleted'.format(file.relative_path))

			return True
		except:
			return False