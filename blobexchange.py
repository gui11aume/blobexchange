# -*- coding: utf-8 -*-


import os
import urllib
import datetime

from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app


class MainHandler(webapp.RequestHandler):
   def get(self):
      upload_url = blobstore.create_upload_url('/upload')
      dot = os.path.dirname(__file__)

      # First fill in the content itself (not the HTML page).
      content_values = {
         'upload_url': upload_url,
      }
      
      content_path = os.path.join(dot, 'content', 'upload_content.html')
      content = template.render(content_path, content_values)

      # Now fill in the HTML page...
      template_path = os.path.join(dot, 'blobexchange_template.html')
      template_values = {
         'page_title': 'Blob Exchange Upload',
         'page_content': content,
      }
      
      # ... and send!
      self.response.out.write(
            template.render(template_path, template_values)
      )


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
   def post(self):
      upload_files = self.get_uploads('file')
      dot = os.path.dirname(__file__)
      blob_info = upload_files[0]
      blob_info.key()

      # First fill in the content itself (not the HTML page).
      content_values = {
         'blob_link': blob_info.key(),
      }
      
      content_path = os.path.join(dot, 'content', 'link_content.html')
      content = template.render(content_path, content_values)

      # Now fill in the HTML page...
      template_path = os.path.join(dot, 'blobexchange_template.html')
      template_values = {
         'page_title': 'Blob Exchange (upload succesful)',
         'page_content': content,
      }
      
      # ... and send!
      self.response.out.write(
            template.render(template_path, template_values)
      )


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
   def get(self, resource):
      resource = str(urllib.unquote(resource))
      blob_info = blobstore.BlobInfo.get(resource)
      self.send_blob(blob_info)


class DeleteHandler(blobstore_handlers.BlobstoreDownloadHandler):
   def get(self):
      three_days_ago = datetime.datetime.today() \
            + datetime.timedelta(days=-3)
      blob_count = blobstore.BlobInfo.all().count()
      all_blobs_query = blobstore.BlobInfo.all().fetch(blob_count)
      for blob in all_blobs_query:
         if blob.creation < three_days_ago:
            blob.delete()


def main():
   application = webapp.WSGIApplication(
        [('/', MainHandler),
         ('/upload', UploadHandler),
         ('/download/([^/]+)?', ServeHandler),
         ('/delete', DeleteHandler),
        ], debug=True)
   run_wsgi_app(application)

if __name__ == '__main__':
   main()
